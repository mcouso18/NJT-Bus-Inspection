from typing import Dict, List, Optional

from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
from pydantic import Field, model_validator


class Manus(ToolCallAgent):
    """A versatile general-purpose agent with support for both local and MCP tools."""

    name: str = "Manus"
    description: str = "A versatile agent that can solve various tasks using multiple tools including MCP-based tools"

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    # MCP clients for remote tool access
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])
    browser_context_helper: Optional[BrowserContextHelper] = None

    # Track connected MCP servers
    connected_servers: Dict[str, str] = Field(
        default_factory=dict
    )  # server_id -> url/command
    _initialized: bool = False

    @model_validator(mode="after")
    def initialize_helper(self) -> "Manus":
        """Initialize basic components synchronously."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "Manus":
        """Factory method to create and properly initialize a Manus instance."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        instance._initialized = True
        return instance

    async def initialize_mcp_servers(self) -> None:
        """Initialize connections to configured MCP servers."""
        for server_id, server_config in config.mcp_config.servers.items():
            try:
                if server_config.type == "sse":
                    if server_config.url:
                        await self.connect_mcp_server(server_config.url, server_id)
                        logger.info(
                            f"Connected to MCP server {server_id} at {server_config.url}"
                        )
                elif server_config.type == "stdio":
                    if server_config.command:
                        await self.connect_mcp_server(
                            server_config.command,
                            server_id,
                            use_stdio=True,
                            stdio_args=server_config.args,
                        )
                        logger.info(
                            f"Connected to MCP server {server_id} using command {server_config.command}"
                        )
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_id}: {e}")

    async def connect_mcp_server(
        self,
        server_url: str,
        server_id: str = "",
        use_stdio: bool = False,
        stdio_args: List[str] = None,
    ) -> None:
        """Connect to an MCP server and add its tools."""
        if use_stdio:
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
            self.connected_servers[server_id or server_url] = server_url
        else:
            await self.mcp_clients.connect_sse(server_url, server_id)
            self.connected_servers[server_id or server_url] = server_url

        # Update available tools with only the new tools from this server
        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """Disconnect from an MCP server and remove its tools."""
        await self.mcp_clients.disconnect(server_id)
        if server_id:
            self.connected_servers.pop(server_id, None)
        else:
            self.connected_servers.clear()

        # Rebuild available tools without the disconnected server's tools
        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        self.available_tools = ToolCollection(*base_tools)
        self.available_tools.add_tools(*self.mcp_clients.tools)

    async def cleanup(self):
        """Clean up Manus agent resources."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
        # Disconnect from all MCP servers only if we were initialized
        if self._initialized:
            await self.disconnect_mcp_server()
            self._initialized = False

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        if not self._initialized:
            await self.initialize_mcp_servers()
            self._initialized = True

        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name == BrowserUseTool().name
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )

        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result

    async def run_vision_analysis(self, vision_prompt: Dict) -> Dict[str, str]:
        """Performs vision analysis and returns structured results for Excel population."""
        logger.info(f"Received vision prompt: {vision_prompt}")

        # Handle text-only prompts that might be mistakenly routed here
        if vision_prompt.get("type") == "text_prompt":
            text_content = vision_prompt.get("text", "")
            logger.info(f"Processing text-only prompt in run_vision_analysis: {text_content}")
            # You might want to call a different LLM for text analysis here
            # For now, return a placeholder or empty dict
            return {"Overall Analysis:": f"Text prompt received: {text_content}"}

        from anthropic import Anthropic

        try:
            vision_config = config.llm.get("vision")
            if not vision_config or not vision_config.api_key or not vision_config.model:
                logger.error("Vision API configuration missing in config.toml")
                return {}

            client = Anthropic(api_key=vision_config.api_key)

            image_data = vision_prompt["image"]
            media_type = image_data["media_type"]
            image_base64 = image_data["data"]

            message = client.messages.create(
                model=vision_config.model,
                max_tokens=vision_config.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {"type": "text", "text": vision_prompt["text"]},
                        ],
                    }
                ],
            )
            claude_response_text = message.content[0].text
            logger.info(f"Vision analysis response: {claude_response_text}")
            self.memory.add_message({"role": "assistant", "content": claude_response_text})

            # FIX: Parse Claude's response into a structured dictionary for Excel
            # This is a placeholder. You NEED to implement _parse_claude_vision_response
            # to extract specific checklist items from claude_response_text.
            parsed_analysis_results = self._parse_claude_vision_response(claude_response_text)
            return parsed_analysis_results

        except Exception as e:
            logger.error(f"Error during vision analysis: {str(e)}")
            return {}

    def _parse_claude_vision_response(self, response_text: str) -> Dict[str, str]:
        """
        Parses the raw text response from Claude Vision into a dictionary
        mapping Excel checklist items to their analysis results.
        This method needs to be implemented based on how you prompt Claude
        and how it structures its responses.
        """
        # This is a crucial placeholder. You need to implement the logic here.
        # Example: If Claude returns JSON, parse it. If it returns natural language,
        # use regex or another LLM call to extract structured data.
        # For demonstration, we'll return a simple mapping based on keywords.

        # IMPORTANT: The keys in this dictionary MUST EXACTLY match the
        # "Checklist Item" names in your Excel template.

        analysis = {}
        if "windshield" in response_text.lower():
            analysis["Windshield"] = "Windshield appears clear."
        if "wipers" in response_text.lower():
            analysis["Windshield Wipers"] = "Wipers are present."
        if "license plate" in response_text.lower():
            analysis["License Plates"] = "License plate detected."
        if "overall" in response_text.lower() or "general condition" in response_text.lower():
            analysis["Overall Analysis:"] = response_text # Use the full response for overall

        # Add more parsing logic here for other checklist items
        # For now, if no specific item is found, put the whole response in Overall Analysis
        if not analysis and response_text:
            analysis["Overall Analysis:"] = response_text

        return analysis
