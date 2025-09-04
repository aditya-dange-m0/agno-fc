"""
Artifact parsing and file creation utilities
Converts TypeScript artifact extraction to Python
"""

import re
import os
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeArtifact:
    """Represents a code artifact extracted from response text"""
    type: Literal['python', 'text', 'json', 'yaml', 'javascript', 'html', 'css']
    filename: str
    purpose: str
    dependencies: Optional[str] = None
    complexity: Literal['simple', 'moderate', 'complex'] = 'simple'
    content: str = ''

def extract_code_artifacts(response_text: str) -> List[CodeArtifact]:
    """
    Extract code artifacts from response text
    Converts the TypeScript version to Python
    """
    artifacts: List[CodeArtifact] = []
    
    logger.info('🔍 EXTRACT_CODE_ARTIFACTS: Starting extraction...')
    logger.info(f'📄 Input text length: {len(response_text)}')
    
    # Regex to match codeartifact XML tags
    artifact_regex = r'<codeartifact\s+([^>]+)>([\s\S]*?)</codeartifact>'
    
    logger.info('🔍 EXTRACT_CODE_ARTIFACTS: Looking for XML codeartifact tags...')
    
    # Test the regex
    test_matches = re.findall(artifact_regex, response_text, re.IGNORECASE)
    logger.info(f'🔍 EXTRACT_CODE_ARTIFACTS: Regex test found {len(test_matches)} matches')
    
    match_count = 0
    
    for match in re.finditer(artifact_regex, response_text, re.IGNORECASE):
        match_count += 1
        logger.info(f'🔍 EXTRACT_CODE_ARTIFACTS: Processing match {match_count}')
        
        attributes_str = match.group(1)
        content = match.group(2).strip()
        
        logger.info(f'📄 Match {match_count} attributes: {attributes_str}')
        logger.info(f'📄 Match {match_count} content length: {len(content)}')
        logger.info(f'📄 Match {match_count} content preview: {content[:100]}...')
        
        # Parse attributes
        attributes: Dict[str, str] = {}
        attr_regex = r'(\w+)="([^"]+)"'
        
        for attr_match in re.finditer(attr_regex, attributes_str):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2)
            attributes[attr_name] = attr_value
            logger.info(f'🔧 Attribute: {attr_name} = "{attr_value}"')
        
        # Create artifact object
        artifact = CodeArtifact(
            type=attributes.get('type', 'text'),
            filename=attributes.get('filename', 'unknown'),
            purpose=attributes.get('purpose', 'unknown'),
            dependencies=attributes.get('dependencies'),
            complexity=attributes.get('complexity', 'simple'),
            content=content
        )
        
        logger.info(f'✅ Created artifact: {artifact.filename} ({artifact.type})')
        artifacts.append(artifact)
    
    logger.info(f'🔍 EXTRACT_CODE_ARTIFACTS: Completed. Found {len(artifacts)} artifacts total')
    
    if len(artifacts) == 0:
        logger.info('⚠️ EXTRACT_CODE_ARTIFACTS: No XML artifacts found, checking for other patterns...')
        
        # Look for any XML-like structures
        xml_patterns = [
            r'<codeartifact[\s\S]*?</codeartifact>',
            r'<artifact[\s\S]*?</artifact>',
            r'<code[\s\S]*?</code>'
        ]
        
        for i, pattern in enumerate(xml_patterns):
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            logger.info(f'🔍 Pattern {i + 1} found {len(matches)} matches')
        
        # Check for markdown code blocks
        markdown_pattern = r'```[\w]*\n([\s\S]*?)\n```'
        markdown_matches = re.findall(markdown_pattern, response_text)
        logger.info(f'🔍 Markdown code blocks found: {len(markdown_matches)}')
        
        if markdown_matches:
            for i, block in enumerate(markdown_matches):
                logger.info(f'📝 Markdown block {i + 1} preview: {block[:100]}...')
    
    return artifacts

def save_artifacts_to_files(artifacts: List[CodeArtifact], base_path: str = "generated") -> List[str]:
    """
    Save code artifacts to physical files
    
    Args:
        artifacts: List of CodeArtifact objects to save
        base_path: Base directory to save files (default: "generated")
    
    Returns:
        List of created file paths
    """
    created_files = []
    
    # Create base directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    logger.info(f'📁 Created/verified base directory: {base_path}')
    
    for i, artifact in enumerate(artifacts):
        try:
            # Determine file path
            file_path = os.path.join(base_path, artifact.filename)
            
            # Create subdirectories if needed
            file_dir = os.path.dirname(file_path)
            if file_dir and file_dir != base_path:
                os.makedirs(file_dir, exist_ok=True)
                logger.info(f'📁 Created subdirectory: {file_dir}')
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(artifact.content)
            
            logger.info(f'✅ Saved artifact {i+1}/{len(artifacts)}: {file_path}')
            logger.info(f'   📋 Purpose: {artifact.purpose}')
            logger.info(f'   🏷️ Type: {artifact.type}')
            logger.info(f'   🔧 Complexity: {artifact.complexity}')
            if artifact.dependencies:
                logger.info(f'   📦 Dependencies: {artifact.dependencies}')
            
            created_files.append(file_path)
            
        except Exception as e:
            logger.error(f'❌ Failed to save artifact {artifact.filename}: {str(e)}')
    
    logger.info(f'🎉 Successfully saved {len(created_files)} out of {len(artifacts)} artifacts')
    return created_files

def create_file_in_sandbox(content: str, filename: str, purpose: str, file_type: str = 'text', base_path: str = "generated") -> str:
    """
    Create a single file in the sandbox/generated directory
    
    Args:
        content: File content
        filename: Name of the file
        purpose: Purpose/description of the file
        file_type: Type of file (python, text, json, etc.)
        base_path: Base directory to save file
    
    Returns:
        Path of the created file
    """
    artifact = CodeArtifact(
        type=file_type,
        filename=filename,
        purpose=purpose,
        content=content
    )
    
    created_files = save_artifacts_to_files([artifact], base_path)
    return created_files[0] if created_files else ""

# Example usage function
def process_backend_response(response_text: str, save_path: str = "generated/backend") -> List[str]:
    """
    Process a backend agent response and save all artifacts
    
    Args:
        response_text: The response from the backend agent
        save_path: Directory to save the generated files
    
    Returns:
        List of created file paths
    """
    logger.info('🚀 Processing backend agent response...')
    
    # Extract artifacts
    artifacts = extract_code_artifacts(response_text)
    
    if not artifacts:
        logger.warning('⚠️ No artifacts found in response')
        return []
    
    # Save to files
    created_files = save_artifacts_to_files(artifacts, save_path)
    
    logger.info(f'✅ Backend processing complete. Created {len(created_files)} files:')
    for file_path in created_files:
        logger.info(f'   📄 {file_path}')
    
    return created_files

if __name__ == "__main__":
    # Test the artifact extraction
    test_response = '''
    Here's your backend code:
    
    <codeartifact type="python" filename="app.py" purpose="Main FastAPI application" complexity="moderate">
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
    </codeartifact>
    
    <codeartifact type="text" filename="requirements.txt" purpose="Python dependencies" complexity="simple">
fastapi==0.104.1
uvicorn==0.24.0
    </codeartifact>
    '''
    
    artifacts = extract_code_artifacts(test_response)
    print(f"Found {len(artifacts)} artifacts")
    
    for artifact in artifacts:
        print(f"- {artifact.filename} ({artifact.type}): {artifact.purpose}")
    
    # Save the artifacts
    if artifacts:
        created_files = save_artifacts_to_files(artifacts, "test_output")
        print(f"Created files: {created_files}")
