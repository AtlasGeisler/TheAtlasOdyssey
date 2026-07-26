/**
 * ChatGPT Integration Module
 * Provides utilities to interact with OpenAI's ChatGPT API
 */

const axios = require('axios');

class ChatGPTIntegration {
  constructor(apiKey = process.env.OPENAI_API_KEY) {
    this.apiKey = apiKey;
    this.model = process.env.OPENAI_MODEL || 'gpt-4';
    this.temperature = parseFloat(process.env.OPENAI_TEMPERATURE || '0.7');
    this.apiEndpoint = 'https://api.openai.com/v1/chat/completions';
  }

  /**
   * Send a message to ChatGPT and get a response
   * @param {string} message - The user message
   * @param {array} conversationHistory - Previous messages for context
   * @returns {Promise<string>} - ChatGPT response
   */
  async chat(message, conversationHistory = []) {
    try {
      const messages = [
        ...conversationHistory,
        { role: 'user', content: message }
      ];

      const response = await axios.post(
        this.apiEndpoint,
        {
          model: this.model,
          messages: messages,
          temperature: this.temperature,
          max_tokens: 2048
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Error calling ChatGPT API:', error.message);
      throw error;
    }
  }

  /**
   * Get code suggestions from ChatGPT
   * @param {string} code - The code to analyze
   * @param {string} context - Additional context about what help is needed
   * @returns {Promise<string>} - ChatGPT suggestions
   */
  async getCodeSuggestions(code, context = '') {
    const prompt = `Please review and suggest improvements for the following code:\n\nContext: ${context}\n\nCode:\n${code}`;
    return this.chat(prompt);
  }

  /**
   * Generate documentation for code
   * @param {string} code - The code to document
   * @returns {Promise<string>} - Generated documentation
   */
  async generateDocumentation(code) {
    const prompt = `Generate comprehensive documentation (comments and docstrings) for the following code:\n\n${code}`;
    return this.chat(prompt);
  }

  /**
   * Find bugs in code
   * @param {string} code - The code to analyze
   * @returns {Promise<string>} - Potential bugs found
   */
  async findBugs(code) {
    const prompt = `Analyze the following code for potential bugs, security issues, and performance problems:\n\n${code}`;
    return this.chat(prompt);
  }
}

module.exports = ChatGPTIntegration;
