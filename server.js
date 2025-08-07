#!/usr/bin/env node

const axios = require('axios');
const readline = require('readline');

const GITLAB_URL = process.env.GITLAB_URL || 'https://gitlab.example.com';
const GITLAB_TOKEN = process.env.GITLAB_TOKEN;
const GITLAB_PROJECT_PATH = process.env.GITLAB_PROJECT_PATH || 'your-group/your-project';

/**
 * Fetch merge request diff
 */
async function fetchMrDiff(mrIid) {
    const encodedPath = encodeURIComponent(GITLAB_PROJECT_PATH);
    const url = `${GITLAB_URL}/api/v4/projects/${encodedPath}/merge_requests/${mrIid}/changes`;
    
    const response = await axios.get(url, {
        headers: {
            'PRIVATE-TOKEN': GITLAB_TOKEN
        }
    });
    
    const data = response.data;
    // Return a clean list of file and diff only
    return (data.changes || []).map(c => ({
        file: c.new_path,
        diff: c.diff
    }));
}

/**
 * Fetch merge request details including diff_refs needed for inline comments
 */
async function fetchMrDetails(mrIid) {
    const encodedPath = encodeURIComponent(GITLAB_PROJECT_PATH);
    const url = `${GITLAB_URL}/api/v4/projects/${encodedPath}/merge_requests/${mrIid}`;
    
    const response = await axios.get(url, {
        headers: {
            'PRIVATE-TOKEN': GITLAB_TOKEN
        }
    });
    
    return response.data;
}

/**
 * Parse diff content to extract valid line numbers for comments
 */
function parseDiffForLineNumbers(diffContent) {
    const lines = diffContent.split('\n');
    const validLines = [];
    let currentNewLine = 0;
    let currentOldLine = 0;

    for (const diffLine of lines) {
        if (diffLine.startsWith('@@')) {
            // Parse hunk header to get starting line numbers
            // Format: @@ -old_start,old_count +new_start,new_count @@
            const match = diffLine.match(/^@@ -(\d+),?\d* \+(\d+),?\d* @@/);
            if (match) {
                currentOldLine = parseInt(match[1], 10);
                currentNewLine = parseInt(match[2], 10);
            }
            continue;
        }

        if (diffLine.startsWith('+') && !diffLine.startsWith('+++')) {
            // This is a new line that can be commented on
            validLines.push({
                type: 'new',
                line_number: currentNewLine,
                content: diffLine.substring(1) // Remove the + prefix
            });
            currentNewLine++;
        } else if (diffLine.startsWith('-') && !diffLine.startsWith('---')) {
            // This is a deleted line that can be commented on
            validLines.push({
                type: 'old',
                line_number: currentOldLine,
                content: diffLine.substring(1) // Remove the - prefix
            });
            currentOldLine++;
        } else if (diffLine.startsWith(' ')) {
            // Context line - both line numbers advance
            currentNewLine++;
            currentOldLine++;
        }
    }

    return validLines;
}

/**
 * Get a list of lines that can be commented on in a merge request
 */
async function getMrCommentableLines(mrIid) {
    const encodedPath = encodeURIComponent(GITLAB_PROJECT_PATH);
    const url = `${GITLAB_URL}/api/v4/projects/${encodedPath}/merge_requests/${mrIid}/changes`;
    
    const response = await axios.get(url, {
        headers: {
            'PRIVATE-TOKEN': GITLAB_TOKEN
        }
    });
    
    const data = response.data;
    const commentableLinesResult = [];

    for (const change of (data.changes || [])) {
        const filePath = change.new_path;
        const diffContent = change.diff;
        const validLines = parseDiffForLineNumbers(diffContent);
        
        commentableLinesResult.push({
            file: filePath,
            commentable_lines: validLines
        });
    }

    return commentableLinesResult;
}

/**
 * Add an inline comment to a merge request
 */
async function addMrInlineComment(mrIid, filePath, lineNumber, commentBody, lineType = 'new') {
    const encodedPath = encodeURIComponent(GITLAB_PROJECT_PATH);
    
    // First, get the merge request details to extract diff_refs
    const mrDetails = await fetchMrDetails(mrIid);
    const diffRefs = mrDetails.diff_refs;
    
    if (!diffRefs) {
        throw new Error('Could not get diff_refs from merge request');
    }

    // Create the position object for the inline comment
    const position = {
        base_sha: diffRefs.base_sha,
        start_sha: diffRefs.start_sha,
        head_sha: diffRefs.head_sha,
        position_type: 'text',
        new_path: filePath
    };

    // Add line number based on type
    if (lineType === 'new') {
        position.new_line = lineNumber;
    } else {
        position.old_line = lineNumber;
        position.old_path = filePath;
    }

    // Create the discussion
    const url = `${GITLAB_URL}/api/v4/projects/${encodedPath}/merge_requests/${mrIid}/discussions`;
    const data = {
        body: commentBody,
        position: position
    };

    const response = await axios.post(url, data, {
        headers: {
            'PRIVATE-TOKEN': GITLAB_TOKEN
        }
    });

    return response.data;
}

/**
 * Add a general comment to a merge request
 */
async function addMrGeneralComment(mrIid, commentBody) {
    const encodedPath = encodeURIComponent(GITLAB_PROJECT_PATH);
    const url = `${GITLAB_URL}/api/v4/projects/${encodedPath}/merge_requests/${mrIid}/notes`;
    
    const data = {
        body: commentBody
    };

    const response = await axios.post(url, data, {
        headers: {
            'PRIVATE-TOKEN': GITLAB_TOKEN
        }
    });

    return response.data;
}

/**
 * Send a JSON response over stdout
 */
function respond(obj) {
    console.log(JSON.stringify(obj));
}

/**
 * Main server loop
 */
async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        crlfDelay: Infinity
    });

    for await (const line of rl) {
        if (!line.trim()) {
            continue;
        }

        let msg;
        try {
            msg = JSON.parse(line);
        } catch (error) {
            continue; // Ignore malformed messages
        }

        const msgType = msg.method;

        try {
            if (msgType === 'initialize') {
                respond({
                    jsonrpc: '2.0',
                    id: msg.id,
                    result: {
                        protocolVersion: '2024-11-05',
                        capabilities: {
                            tools: {}
                        },
                        serverInfo: {
                            name: 'Private GitLab MCP',
                            version: '0.1.0'
                        }
                    }
                });
            } else if (msgType === 'tools/list') {
                respond({
                    jsonrpc: '2.0',
                    id: msg.id,
                    result: {
                        tools: [
                            {
                                name: 'hello_world',
                                description: 'Returns a friendly hello message',
                                inputSchema: {
                                    type: 'object',
                                    properties: {},
                                    required: []
                                }
                            },
                            {
                                name: 'fetch_merge_request_diff',
                                description: 'Fetches the diff of a given merge request for a GitLab project',
                                inputSchema: {
                                    type: 'object',
                                    properties: {
                                        project_path: { type: 'string' },
                                        mr_iid: { type: 'integer' }
                                    },
                                    required: ['project_path', 'mr_iid']
                                }
                            },
                            {
                                name: 'add_merge_request_inline_comment',
                                description: 'Adds an inline comment to a specific line in a merge request diff',
                                inputSchema: {
                                    type: 'object',
                                    properties: {
                                        project_path: { type: 'string', description: 'GitLab project path' },
                                        mr_iid: { type: 'integer', description: 'Merge request IID' },
                                        file_path: { type: 'string', description: 'Path to the file in the diff' },
                                        line_number: { type: 'integer', description: 'Line number to comment on' },
                                        comment_body: { type: 'string', description: 'The comment text' },
                                        line_type: {
                                            type: 'string',
                                            enum: ['new', 'old'],
                                            default: 'new',
                                            description: 'Whether to comment on new line (added) or old line (removed)'
                                        }
                                    },
                                    required: ['project_path', 'mr_iid', 'file_path', 'line_number', 'comment_body']
                                }
                            },
                            {
                                name: 'get_merge_request_commentable_lines',
                                description: 'Gets a list of lines that can be commented on in a merge request diff',
                                inputSchema: {
                                    type: 'object',
                                    properties: {
                                        project_path: { type: 'string', description: 'GitLab project path' },
                                        mr_iid: { type: 'integer', description: 'Merge request IID' }
                                    },
                                    required: ['project_path', 'mr_iid']
                                }
                            },
                            {
                                name: 'add_merge_request_general_comment',
                                description: 'Adds a general comment to a merge request (appears in Overview tab)',
                                inputSchema: {
                                    type: 'object',
                                    properties: {
                                        project_path: { type: 'string', description: 'GitLab project path' },
                                        mr_iid: { type: 'integer', description: 'Merge request IID' },
                                        comment_body: { type: 'string', description: 'The comment text' }
                                    },
                                    required: ['project_path', 'mr_iid', 'comment_body']
                                }
                            }
                        ]
                    }
                });
            } else if (msgType === 'tools/call') {
                const toolName = msg.params?.name;
                const args = msg.params?.arguments || {};

                if (toolName === 'hello_world') {
                    respond({
                        jsonrpc: '2.0',
                        id: msg.id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: 'Hello from your Private GitLab MCP!'
                                }
                            ]
                        }
                    });
                } else if (toolName === 'fetch_merge_request_diff') {
                    const mrIid = args.mr_iid;
                    const result = await fetchMrDiff(mrIid);
                    respond({
                        jsonrpc: '2.0',
                        id: msg.id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: JSON.stringify(result, null, 2)
                                }
                            ]
                        }
                    });
                } else if (toolName === 'add_merge_request_inline_comment') {
                    const { mr_iid, file_path, line_number, comment_body, line_type = 'new' } = args;
                    
                    if (!mr_iid || !file_path || !line_number || !comment_body) {
                        throw new Error('Missing required parameters');
                    }
                    
                    const result = await addMrInlineComment(mr_iid, file_path, line_number, comment_body, line_type);
                    respond({
                        jsonrpc: '2.0',
                        id: msg.id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: `Successfully added inline comment to ${file_path} at line ${line_number}. Discussion ID: ${result.id}`
                                }
                            ]
                        }
                    });
                } else if (toolName === 'get_merge_request_commentable_lines') {
                    const mrIid = args.mr_iid;
                    
                    if (!mrIid) {
                        throw new Error('Missing required parameter: mr_iid');
                    }
                    
                    const result = await getMrCommentableLines(mrIid);
                    respond({
                        jsonrpc: '2.0',
                        id: msg.id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: JSON.stringify(result, null, 2)
                                }
                            ]
                        }
                    });
                } else if (toolName === 'add_merge_request_general_comment') {
                    const { mr_iid, comment_body } = args;
                    
                    if (!mr_iid || !comment_body) {
                        throw new Error('Missing required parameters: mr_iid and comment_body');
                    }
                    
                    const result = await addMrGeneralComment(mr_iid, comment_body);
                    respond({
                        jsonrpc: '2.0',
                        id: msg.id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: `Successfully added general comment to merge request ${mr_iid}. Note ID: ${result.id}`
                                }
                            ]
                        }
                    });
                } else {
                    throw new Error(`Unknown tool: ${toolName}`);
                }
            } else {
                respond({
                    jsonrpc: '2.0',
                    id: msg.id,
                    error: {
                        code: -32601,
                        message: `Unknown message type: ${msgType}`
                    }
                });
            }
        } catch (error) {
            respond({
                jsonrpc: '2.0',
                id: msg.id,
                error: {
                    code: -32603,
                    message: error.message
                }
            });
        }
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error('Server error:', error);
        process.exit(1);
    });
}

module.exports = {
    fetchMrDiff,
    addMrGeneralComment,
    main
};