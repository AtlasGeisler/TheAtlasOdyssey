/**
 * Example usage of ChatGPT Integration
 */

require('dotenv').config();
const ChatGPTIntegration = require('./chatgpt-integration');

async function main() {
  const chatgpt = new ChatGPTIntegration();

  try {
    // Example 1: Simple chat
    console.log('=== Simple Chat ===');
    const response = await chatgpt.chat('What is the best practice for error handling in JavaScript?');
    console.log('Response:', response);

    // Example 2: Get code suggestions
    console.log('\n=== Code Suggestions ===');
    const sampleCode = `
function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total = total + items[i].price;
  }
  return total;
}
    `;
    const suggestions = await chatgpt.getCodeSuggestions(sampleCode, 'Improve efficiency and readability');
    console.log('Suggestions:', suggestions);

    // Example 3: Generate documentation
    console.log('\n=== Generated Documentation ===');
    const documentation = await chatgpt.generateDocumentation(sampleCode);
    console.log('Documentation:', documentation);

    // Example 4: Find bugs
    console.log('\n=== Bug Analysis ===');
    const buggyCode = `
function getUserById(users, id) {
  return users[id];
}
    `;
    const bugs = await chatgpt.findBugs(buggyCode);
    console.log('Bug Analysis:', bugs);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
