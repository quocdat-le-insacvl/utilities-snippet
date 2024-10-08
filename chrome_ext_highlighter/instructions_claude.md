# Translate Highlighted Words

Translate highlighted words from the provided text, considering their context.

## CSV File Format

Create a CSV file with the following columns in this exact order:
1. **English Word/Phrase**: Include the word as it appears, followed by its base form (if different), separated by " / "
2. **Vietnamese Translation**: Provide the primary translation, followed by alternatives if helpful, separated by " / "
3. **Context**: The full sentence or phrase containing the word, enclosed in quotes. Ensure the target word is included and accurately represented.

## CSV Generation Guidelines

- Do not include a header row
- Start data from the first line
- Ensure strict adherence to the specified format
- Process all words enclosed in ** ** from the text
- Produce only the CSV content, without additional explanations
- Double-check each entry for accuracy, especially the context

## Example CSV Entries

```code
rushed / rush,lao về phía / xông tới,"He **rushed** towards her as if to save her from drowning."
serendipitous,tình cờ may mắn / bất ngờ và đáng mừng,"Their meeting was entirely **serendipitous**, yet it changed both their lives."
oscillating / oscillate,dao động / lắc lư,"The fan was **oscillating** slowly, spreading cool air throughout the room."
cognizant / cognizance,nhận thức được / ý thức,"She was fully **cognizant** of the risks involved in the experiment."
paradigm,mô hình / khuôn mẫu,"This discovery represents a **paradigm** shift in our understanding of quantum physics."
```

## Additional Instructions

- For verbs, include both the conjugated form and the infinitive
- For nouns or adjectives with multiple forms, include all relevant forms
- Provide context that clearly demonstrates the word's usage and meaning
- If a word has multiple meanings, prioritize the one used in the given context
- Ensure all translations are accurate and appropriate for the context
- Verify that the context provided for each word is correct and directly from the original text

## Output Requirements

- Verify that all words enclosed in ** ** are included
- Double-check format compliance for each entry
- Ensure translations accurately reflect the contextual meaning
- Provide only the CSV content for easy copying and use
- Use artifact code to present the CSV content
- After generating the CSV, review each entry to confirm the context is accurate and matches the original text

## Quality Control

- After completing the CSV, randomly select 5-10 entries and cross-reference them with the original text to ensure accuracy
- If any errors are found during this check, review and correct all entries before finalizing the CSV
- If asked to update or correct an entry, carefully review the entire CSV again to ensure no other similar errors exist

When you have processed the text and created the CSV file, please provide the entire CSV content within an artifact, similar to the example entries provided above. Always be prepared to make corrections if errors are pointed out.

----------------------------------------------------------------------------------------------------------------

