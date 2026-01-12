// Generate smart conversation titles from user messages

export const generateConversationTitle = (message: string): string => {
  // Clean the message
  const cleaned = message.trim();
  
  // If message is too short, use a default pattern
  if (cleaned.length < 10) {
    return "New Chat";
  }
  
  // Extract first sentence or up to 50 characters
  let title = cleaned;
  
  // Find first sentence ending
  const sentenceEnd = cleaned.match(/[.!?]/);
  if (sentenceEnd && sentenceEnd.index && sentenceEnd.index < 60) {
    title = cleaned.substring(0, sentenceEnd.index);
  } else {
    // Take first 50 characters
    title = cleaned.substring(0, 50);
  }
  
  // Remove markdown formatting
  title = title.replace(/[#*`_~\[\]]/g, '');
  
  // Remove extra whitespace
  title = title.replace(/\s+/g, ' ').trim();
  
  // Capitalize first letter
  title = title.charAt(0).toUpperCase() + title.slice(1);
  
  // Add ellipsis if truncated
  if (title.length < cleaned.length && title.length >= 40) {
    title += '...';
  }
  
  // Limit to 60 characters max
  if (title.length > 60) {
    title = title.substring(0, 60) + '...';
  }
  
  return title || "New Chat";
};

// Generate title using common question patterns
export const generateSmartTitle = (message: string): string => {
  const cleaned = message.trim().toLowerCase();
  
  // Common patterns and their short titles
  const patterns: [RegExp, string][] = [
    [/^(what is|what are|what's)\s+(.+?)[\?\.]/i, "About $2"],
    [/^(how to|how do i|how can i)\s+(.+?)[\?\.]/i, "How to $2"],
    [/^(why (is|are|do|does))\s+(.+?)[\?\.]/i, "Why $3"],
    [/^(when (is|are|do|does))\s+(.+?)[\?\.]/i, "When $3"],
    [/^(where (is|are|do|does))\s+(.+?)[\?\.]/i, "Where $3"],
    [/^(can you|could you)\s+(.+?)[\?\.]/i, "$2"],
    [/^(tell me about|explain)\s+(.+?)[\?\.]/i, "About $2"],
    [/^(help me|help with)\s+(.+?)[\?\.]/i, "Help with $2"],
    [/^(create|make|build)\s+(.+?)[\?\.]/i, "Create $2"],
    [/^(write|draft)\s+(.+?)[\?\.]/i, "Write $2"],
  ];
  
  // Try to match patterns
  for (const [pattern, replacement] of patterns) {
    const match = message.match(pattern);
    if (match) {
      let title = message.replace(pattern, replacement);
      title = title.replace(/[#*`_~\[\]]/g, '').trim();
      title = title.charAt(0).toUpperCase() + title.slice(1);
      
      if (title.length > 50) {
        title = title.substring(0, 50) + '...';
      }
      
      return title;
    }
  }
  
  // Fall back to simple extraction
  return generateConversationTitle(message);
};

