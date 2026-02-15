"""
Output Formatters - Generate Anthropic SKILL and Continue SlashCMD formats
"""

import os
import zipfile
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET
from xml.dom import minidom

from .models import SkillDescriptor


class AnthropicSkillFormatter:
    """
    Formatter for Anthropic SKILL packages.
    Creates .zip files compatible with Claude Code and Cline.
    """
    
    def format(self, skill: SkillDescriptor, output_path: str) -> str:
        """
        Format a skill as an Anthropic SKILL package.
        
        Args:
            skill: SkillDescriptor to format
            output_path: Path for output .zip file (without extension)
            
        Returns:
            Path to created .zip file
        """
        # Ensure .zip extension
        if not output_path.endswith('.zip'):
            output_path += '.zip'
        
        # Create temporary directory for package contents
        temp_dir = Path(output_path).parent / f"_temp_{skill.name}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Generate prompt.xml
            prompt_xml = self._generate_prompt_xml(skill)
            (temp_dir / "prompt.xml").write_text(prompt_xml, encoding='utf-8')
            
            # Generate instructions.md
            instructions_md = self._generate_instructions(skill)
            (temp_dir / "instructions.md").write_text(instructions_md, encoding='utf-8')
            
            # Create examples directory if there are examples
            if skill.examples:
                examples_dir = temp_dir / "examples"
                examples_dir.mkdir(exist_ok=True)
                
                for i, example in enumerate(skill.examples):
                    (examples_dir / f"example_{i+1}.md").write_text(
                        example, encoding='utf-8'
                    )
            
            # Create ZIP package
            self.create_zip(temp_dir, output_path)
            
            return output_path
        
        finally:
            # Cleanup temp directory
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def _generate_prompt_xml(self, skill: SkillDescriptor) -> str:
        """Generate prompt.xml for Anthropic SKILL."""
        root = ET.Element('prompt')
        
        # Skill metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'name').text = skill.name
        ET.SubElement(metadata, 'description').text = skill.description
        
        # Skill instructions
        instructions = ET.SubElement(root, 'instructions')
        
        # What
        what_elem = ET.SubElement(instructions, 'section', name='what')
        what_elem.text = skill.what
        
        # Why
        why_elem = ET.SubElement(instructions, 'section', name='why')
        why_elem.text = skill.why
        
        # How
        how_elem = ET.SubElement(instructions, 'section', name='how')
        steps_elem = ET.SubElement(how_elem, 'steps')
        for step in skill.how:
            step_elem = ET.SubElement(steps_elem, 'step', order=str(step.order))
            ET.SubElement(step_elem, 'action').text = step.action
            ET.SubElement(step_elem, 'reasoning').text = step.reasoning
        
        # When
        if skill.when:
            when_elem = ET.SubElement(instructions, 'section', name='when')
            for context in skill.when:
                ET.SubElement(when_elem, 'context').text = context
        
        # Constraints
        if skill.constraints:
            constraints_elem = ET.SubElement(instructions, 'section', name='constraints')
            for constraint in skill.constraints:
                ET.SubElement(constraints_elem, 'constraint').text = constraint
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    def _generate_instructions(self, skill: SkillDescriptor) -> str:
        """Generate instructions.md for the skill."""
        lines = [
            f"# {skill.name}",
            "",
            skill.description,
            "",
            "## What",
            "",
            skill.what,
            "",
            "## Why",
            "",
            skill.why,
            "",
            "## How",
            "",
        ]
        
        for step in skill.how:
            lines.append(f"{step.order}. **{step.action}**")
            lines.append(f"   - Reasoning: {step.reasoning}")
            lines.append("")
        
        if skill.when:
            lines.extend([
                "## When to Use",
                "",
            ])
            for context in skill.when:
                lines.append(f"- {context}")
            lines.append("")
        
        if skill.examples:
            lines.extend([
                "## Examples",
                "",
                "See the `examples/` directory for detailed examples.",
                "",
            ])
        
        if skill.constraints:
            lines.extend([
                "## Constraints & Preconditions",
                "",
            ])
            for constraint in skill.constraints:
                lines.append(f"- {constraint}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def create_zip(self, source_dir: Path, output_path: str):
        """Create ZIP archive from directory."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)


class ContinueSlashCMDFormatter:
    """
    Formatter for Continue VSCode extension slash commands.
    Creates .md files with YAML frontmatter.
    """
    
    def format(self, skill: SkillDescriptor, output_path: str) -> str:
        """
        Format a skill as a Continue slash command.
        
        Args:
            skill: SkillDescriptor to format
            output_path: Path for output .md file
            
        Returns:
            Path to created .md file
        """
        # Ensure .md extension
        if not output_path.endswith('.md'):
            output_path += '.md'
        
        content = self._generate_slash_command(skill)
        
        # Create parent directories if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _generate_slash_command(self, skill: SkillDescriptor) -> str:
        """Generate Continue slash command markdown."""
        lines = [
            "---",
            f"name: {skill.name}",
            f"description: {skill.description}",
            "invokable: true",
            "---",
            "",
            "# Task@WHAT",
            "",
            skill.what,
            "",
            f"**When to use this skill:**",
        ]
        
        if skill.when:
            for context in skill.when:
                lines.append(f"- {context}")
        else:
            lines.append("- When applicable to your task")
        
        lines.extend([
            "",
            "## Purpose@WHY",
            "",
            skill.why,
            "",
        ])
        
        if skill.constraints:
            lines.extend([
                "**Important considerations:**",
            ])
            for constraint in skill.constraints:
                lines.append(f"- {constraint}")
            lines.append("")
        
        lines.extend([
            "## Steps@HOW",
            "",
            "Follow these steps systematically:",
            "",
        ])
        
        for step in skill.how:
            lines.extend([
                f"### Step {step.order}: {step.action}",
                "",
                f"**Reasoning:** {step.reasoning}",
                "",
            ])
        
        if skill.examples:
            lines.extend([
                "## Examples",
                "",
            ])
            for i, example in enumerate(skill.examples, 1):
                lines.extend([
                    f"### Example {i}",
                    "",
                    example,
                    "",
                ])
        
        lines.extend([
            "## One-More-Thing",
            "",
            "**STOP and verify** if you encounter:",
            "- Any confusion or ambiguity in the requirements",
            "- Missing information needed to complete the task",
            "- Potential conflicts with existing code or patterns",
            "",
            "Ask the user to clarify before proceeding with execution.",
            "",
        ])
        
        return '\n'.join(lines)
    
    def write_file(self, content: str, output_path: str):
        """Write content to file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def save_skills_json(skills: List[SkillDescriptor], output_path: str) -> str:
    """
    Save skills to JSON file for inspection/editing.
    
    Args:
        skills: List of SkillDescriptors
        output_path: Path for output JSON file
        
    Returns:
        Path to created JSON file
    """
    import json
    
    # Ensure .json extension
    if not output_path.endswith('.json'):
        output_path += '.json'
    
    # Create parent directories if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert skills to dicts
    skills_data = [skill.to_dict() for skill in skills]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(skills_data, f, indent=2, ensure_ascii=False)
    
    return output_path
