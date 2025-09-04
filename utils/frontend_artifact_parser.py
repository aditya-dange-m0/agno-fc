"""
Frontend-specific artifact parsing and file creation utilities
Based on the TypeScript extractFrontendCodeArtifacts logic
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
class FrontendCodeArtifact:
    """Represents a frontend code artifact extracted from response text"""
    type: Literal['react', 'javascript', 'typescript', 'css', 'json', 'html']
    filename: str
    purpose: str
    dependencies: Optional[str] = None
    complexity: Literal['simple', 'moderate', 'complex'] = 'simple'
    framework: Literal['react', 'nextjs', 'vite'] = 'react'
    content: str = ''

def get_artifact_type(filename: str) -> Literal['react', 'javascript', 'typescript', 'css', 'json', 'html']:
    """Determine artifact type based on file extension"""
    if filename.endswith('.tsx') or filename.endswith('.jsx'):
        return 'react'
    elif filename.endswith('.ts'):
        return 'typescript'
    elif filename.endswith('.js'):
        return 'javascript'
    elif filename.endswith('.css'):
        return 'css'
    elif filename.endswith('.json'):
        return 'json'
    elif filename.endswith('.html'):
        return 'html'
    else:
        return 'react'  # Default

def assess_code_complexity(content: str) -> Literal['simple', 'moderate', 'complex']:
    """Assess code complexity based on content analysis"""
    lines = content.count('\n')
    if lines < 50:
        return 'simple'
    elif lines < 200:
        return 'moderate'
    else:
        return 'complex'

def extract_frontend_code_artifacts(response_text: str) -> List[FrontendCodeArtifact]:
    """
    Extract frontend code artifacts from response text
    Based on the TypeScript extractFrontendCodeArtifacts function
    """
    artifacts: List[FrontendCodeArtifact] = []
    
    logger.info('🔍 EXTRACT_FRONTEND_CODE_ARTIFACTS: Starting extraction...')
    logger.info(f'📄 Input text length: {len(response_text)}')
    
    # Primary: Extract <codeartifact> tags (as used in frontend prompt)
    code_artifact_regex = r'<codeartifact\s+([^>]+)>([\s\S]*?)</codeartifact>'
    
    logger.info('🔍 Looking for <codeartifact> tags...')
    
    for match in re.finditer(code_artifact_regex, response_text, re.IGNORECASE):
        attributes_str = match.group(1)
        content = match.group(2).strip()
        
        # Clean markdown formatting from content if present
        content = clean_markdown_content(content)
        
        logger.info(f'📄 Found codeartifact: {attributes_str}')
        logger.info(f'📄 Content length: {len(content)}')
        
        # Parse attributes
        attributes: Dict[str, str] = {}
        attr_regex = r'(\w+)="([^"]+)"'
        
        for attr_match in re.finditer(attr_regex, attributes_str):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2)
            attributes[attr_name] = attr_value
        
        # Create artifact object
        artifact = FrontendCodeArtifact(
            type=attributes.get('type', 'react'),
            filename=attributes.get('filename', 'unknown'),
            purpose=attributes.get('purpose', 'unknown'),
            dependencies=attributes.get('dependencies'),
            complexity=attributes.get('complexity', 'simple'),
            framework=attributes.get('framework', 'react'),
            content=content
        )
        
        logger.info(f'✅ Created frontend artifact: {artifact.filename} ({artifact.type})')
        artifacts.append(artifact)
    
    # Fallback: Extract <file> tags (similar to route.ts)
    if len(artifacts) == 0:
        logger.info('🔍 No <codeartifact> tags found, looking for <file> tags...')
        
        file_regex = r'<file\s+path="([^"]+)"[^>]*>([\s\S]*?)</file>'
        
        for match in re.finditer(file_regex, response_text, re.IGNORECASE):
            file_path = match.group(1)
            content = match.group(2).strip()
            
            if file_path and content:
                # Clean markdown formatting from content
                content = clean_markdown_content(content)
                
                # Determine artifact type based on file extension
                artifact_type = get_artifact_type(file_path)
                complexity = assess_code_complexity(content)
                
                artifact = FrontendCodeArtifact(
                    type=artifact_type,
                    filename=file_path,
                    purpose=f'Generated {artifact_type} file',
                    complexity=complexity,
                    framework='react',
                    content=content
                )
                
                logger.info(f'✅ Created frontend artifact from <file>: {artifact.filename}')
                artifacts.append(artifact)
    
    # Additional fallback: Extract code blocks with filename comments
    if len(artifacts) == 0:
        logger.info('🔍 No XML tags found, looking for code blocks with filenames...')
        
        code_block_pattern = r'```(?:typescript|tsx|jsx|javascript|css|json)?\s*(?://\s*([^\n]+\.(?:tsx?|jsx?|css|json))|/\*\s*([^\*]+\.(?:tsx?|jsx?|css|json))\s*\*/)?\s*([\s\S]*?)```'
        
        file_index = 1
        for match in re.finditer(code_block_pattern, response_text, re.IGNORECASE):
            filename = match.group(1) or match.group(2) or f'Component{file_index}.tsx'
            content = match.group(3).strip()
            
            if content:
                # Clean markdown formatting from content
                content = clean_markdown_content(content)
                
                artifact_type = get_artifact_type(filename)
                complexity = assess_code_complexity(content)
                
                artifact = FrontendCodeArtifact(
                    type=artifact_type,
                    filename=filename,
                    purpose=f'Generated {artifact_type} file',
                    complexity=complexity,
                    framework='react',
                    content=content
                )
                
                logger.info(f'✅ Created frontend artifact from code block: {artifact.filename}')
                artifacts.append(artifact)
                file_index += 1
    
    logger.info(f'🔍 EXTRACT_FRONTEND_CODE_ARTIFACTS: Completed. Found {len(artifacts)} artifacts total')
    return artifacts

def clean_markdown_content(content: str) -> str:
    """
    Clean markdown code blocks from content if present
    
    Args:
        content: Raw content that might contain markdown code blocks
        
    Returns:
        Cleaned content without markdown formatting
    """
    # Remove starting markdown code block markers
    content = re.sub(r'^````?\w*\s*\n?', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```\w*\s*\n?', '', content, flags=re.MULTILINE)
    
    # Remove ending markdown code block markers
    content = re.sub(r'\n?````?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n?```\s*$', '', content, flags=re.MULTILINE)
    
    return content.strip()

def save_frontend_artifacts_to_files(artifacts: List[FrontendCodeArtifact], base_path: str = "generated/frontend") -> List[str]:
    """
    Save frontend code artifacts to physical files
    
    Args:
        artifacts: List of FrontendCodeArtifact objects to save
        base_path: Base directory to save files (default: "generated/frontend")
    
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
            
            # Clean the content of any markdown formatting
            clean_content = clean_markdown_content(artifact.content)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            logger.info(f'✅ Saved frontend artifact {i+1}/{len(artifacts)}: {file_path}')
            logger.info(f'   📋 Purpose: {artifact.purpose}')
            logger.info(f'   🏷️ Type: {artifact.type}')
            logger.info(f'   🎯 Framework: {artifact.framework}')
            logger.info(f'   🔧 Complexity: {artifact.complexity}')
            if artifact.dependencies:
                logger.info(f'   📦 Dependencies: {artifact.dependencies}')
            
            created_files.append(file_path)
            
        except Exception as e:
            logger.error(f'❌ Failed to save frontend artifact {artifact.filename}: {str(e)}')
    
    logger.info(f'🎉 Successfully saved {len(created_files)} out of {len(artifacts)} frontend artifacts')
    return created_files

def process_frontend_response(response_text: str, save_path: str = "generated/frontend") -> List[str]:
    """
    Process a frontend agent response and save all artifacts
    
    Args:
        response_text: The response from the frontend agent
        save_path: Directory to save the generated files
    
    Returns:
        List of created file paths
    """
    logger.info('🚀 Processing frontend agent response...')
    
    # Extract artifacts
    artifacts = extract_frontend_code_artifacts(response_text)
    
    if not artifacts:
        logger.warning('⚠️ No frontend artifacts found in response')
        return []
    
    # Save to files
    created_files = save_frontend_artifacts_to_files(artifacts, save_path)
    
    logger.info(f'✅ Frontend processing complete. Created {len(created_files)} files:')
    for file_path in created_files:
        logger.info(f'   📄 {file_path}')
    
    return created_files

def clean_existing_frontend_files(directory_path: str) -> List[str]:
    """
    Clean existing frontend files that contain markdown code blocks
    
    Args:
        directory_path: Path to the directory containing frontend files to clean
        
    Returns:
        List of cleaned file paths
    """
    cleaned_files = []
    
    if not os.path.exists(directory_path):
        logger.warning(f'⚠️ Directory does not exist: {directory_path}')
        return cleaned_files
    
    logger.info(f'🧹 Starting cleanup of frontend files in: {directory_path}')
    
    # Find all relevant frontend files
    frontend_extensions = ['.tsx', '.jsx', '.ts', '.js', '.css', '.json']
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.endswith(ext) for ext in frontend_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    # Read current content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file contains markdown code blocks
                    if '```' in content or '````' in content:
                        logger.info(f'🔧 Cleaning markdown from: {file_path}')
                        
                        # Clean the content
                        cleaned_content = clean_markdown_content(content)
                        
                        # Write back the cleaned content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        
                        cleaned_files.append(file_path)
                        logger.info(f'✅ Cleaned: {file_path}')
                    else:
                        logger.info(f'✨ Already clean: {file_path}')
                        
                except Exception as e:
                    logger.error(f'❌ Failed to clean {file_path}: {str(e)}')
    
    logger.info(f'🎉 Cleanup complete. Processed {len(cleaned_files)} files')
    return cleaned_files

def clean_existing_frontend_files(directory_path: str) -> List[str]:
    """
    Clean existing frontend files that contain markdown code blocks
    
    Args:
        directory_path: Path to the directory containing files to clean
        
    Returns:
        List of cleaned file paths
    """
    cleaned_files = []
    
    if not os.path.exists(directory_path):
        logger.warning(f'⚠️ Directory does not exist: {directory_path}')
        return cleaned_files
    
    # Find all relevant frontend files
    frontend_extensions = ['.tsx', '.jsx', '.ts', '.js', '.css', '.json']
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.endswith(ext) for ext in frontend_extensions):
                file_path = os.path.join(root, file)
                
                try:
                    # Read current content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if content has markdown formatting
                    if '```' in content or '````' in content:
                        logger.info(f'🧹 Cleaning markdown from: {file_path}')
                        
                        # Clean the content
                        cleaned_content = clean_markdown_content(content)
                        
                        # Write back cleaned content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        
                        cleaned_files.append(file_path)
                        logger.info(f'✅ Cleaned: {file_path}')
                    
                except Exception as e:
                    logger.error(f'❌ Failed to clean file {file_path}: {str(e)}')
    
    logger.info(f'🎉 Cleaned {len(cleaned_files)} frontend files')
    return cleaned_files

if __name__ == "__main__":
    # Test the frontend artifact extraction
    test_response = '''
    Here's your React component:
    
    <codeartifact type="react" filename="App.tsx" purpose="Main React application component" framework="react" complexity="moderate" dependencies="react, tailwindcss">
import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Hello World</h1>
        <p className="text-gray-600">Welcome to your React app!</p>
      </div>
    </div>
  );
}

export default App;
    </codeartifact>
    
    <codeartifact type="json" filename="package.json" purpose="NPM package configuration" framework="react" complexity="simple">
{
  "name": "my-react-app",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
    </codeartifact>
    '''
    
    artifacts = extract_frontend_code_artifacts(test_response)
    print(f"Found {len(artifacts)} frontend artifacts")
    
    for artifact in artifacts:
        print(f"- {artifact.filename} ({artifact.type}, {artifact.framework}): {artifact.purpose}")
    
    # Save the artifacts
    if artifacts:
        created_files = save_frontend_artifacts_to_files(artifacts, "test_frontend_output")
        print(f"Created frontend files: {created_files}")
    
    # Test cleaning existing files
    print("\nTesting file cleaning...")
    frontend_dir = "d:/code-generation/v3/agents/generated/frontend"
    if os.path.exists(frontend_dir):
        cleaned = clean_existing_frontend_files(frontend_dir)
        print(f"Cleaned files: {cleaned}")
    else:
        print(f"Frontend directory not found: {frontend_dir}")
    
    # Test cleaning existing files
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        directory = sys.argv[2] if len(sys.argv) > 2 else "generated/frontend"
        cleaned_files = clean_existing_frontend_files(directory)
        print(f"Cleaned {len(cleaned_files)} files")
