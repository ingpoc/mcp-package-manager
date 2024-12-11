"""Response utility functions for package management."""

import logging
from typing import List
from mcp.types import TextContent

logger = logging.getLogger(__name__)

def create_text_response(message: str) -> List[TextContent]:
    """Create a TextContent response.
    
    Args:
        message: Message text
        
    Returns:
        List[TextContent]: Formatted response
    """
    try:
        return [TextContent(text=message)]
    except Exception as e1:
        try:
            return [TextContent(**{"text": message, "type": "text"})]
        except Exception as e2:
            logger.error(f"Error creating TextContent: {e1}, {e2}")
            return [TextContent(text=message, type="text")]