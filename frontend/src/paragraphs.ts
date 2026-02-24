export const paragraphsByAge: Record<number, string[]> = {
  5: [
    "The cat sat on the mat and looked at the sun."
  ],
  6: [
    "A little dog ran through the park and played with a big ball.",
    "The bird sat on the branch and sang a happy song."
  ],
  7: [
    "One sunny morning, a small rabbit hopped down the forest path to find some fresh carrots.",
    "The children played games at school and had fun with their friends all day long."
  ],
  8: [
    "An old farmer walked through his fields early in the morning to check on his plants and animals.",
    "Sarah opened her favorite book and began to read about a magical kingdom far away."
  ],
  9: [
    "The ancient library contained thousands of books about history, science, and adventure stories from around the world.",
    "During the thunderstorm, the children watched lightning flash across the dark sky while listening to the loud thunder."
  ],
  10: [
    "Scientific research has shown that reading regularly improves vocabulary and helps develop better concentration and imagination.",
    "The explorers discovered a hidden waterfall deep in the rainforest surrounded by exotic plants and colorful animals."
  ],
  12: [
    "Technology has revolutionized the way we communicate and access information, making knowledge available to nearly everyone with an internet connection.",
    "Mediterranean countries have developed a unique farming tradition using terraced lands to grow olives, grapes, and other agricultural products."
  ],
  14: [
    "Neuroplasticity, the brain's ability to reorganize neural pathways and create new connections, demonstrates how consistent practice can enhance cognitive abilities and learning capacity.",
    "The Renaissance period marked a significant shift in European art and culture, emphasizing humanism, individualism, and a revival of classical knowledge from ancient Greece and Rome."
  ],
  16: [
    "The interdisciplinary study of environmental science addresses complex challenges including climate change, biodiversity conservation, sustainable resource management, and the interrelationship between human societies and natural ecosystems.",
    "Literary analysis requires understanding not only the literal meaning of a text but also recognizing symbolism, identifying authorial intent, analyzing narrative structure, and examining how language and imagery contribute to thematic development."
  ],
  18: [
    "Epistemological frameworks in contemporary philosophy examine the nature of knowledge, justification, and truth, exploring fundamental questions about how we can acquire reliable information and distinguish between justified belief and genuine understanding.",
    "Quantum mechanics fundamentally challenges classical physics by introducing probabilistic interpretations of reality, demonstrating that observation affects quantum systems, and revealing phenomena such as superposition and entanglement that have profound implications for our understanding of the universe."
  ]
};

export function getParagraphForAge(age: number): string {
  // Find the closest age group
  const ages = Object.keys(paragraphsByAge).map(Number).sort((a, b) => a - b);
  const closestAge = ages.reduce((prev, curr) => 
    Math.abs(curr - age) < Math.abs(prev - age) ? curr : prev
  );
  
  const paragraphs = paragraphsByAge[closestAge];
  return paragraphs[Math.floor(Math.random() * paragraphs.length)];
}
