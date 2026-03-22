# SaveAsSkill

## User Story

- 【AS A】 GitHub Copilot Chat User,
- 【I WANT TO】 save the current conversation as a skill,
  - 【WHEN】 I finally solve the problem after a long long conversation,
- 【SO THAT】 I can reuse the solution as a skill in the future.

## Acceptance Criteria

- 【GIVEN】 I have a conversation with GitHub Copilot Chat,
- 【WHEN】 I call slash command `/save-as-skill` in the chat input box,
- 【THEN】 I should see a new skill created from the current conversation, 
  - OR if the conversation is not enough to create a skill, I should see an advice message such as:
    - "too simple to be a skill, save as rule or workflow instead"
  - AND the new skill should follow anthropic's skill specification.

