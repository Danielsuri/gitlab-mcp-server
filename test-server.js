#!/usr/bin/env node

const axios = require('axios');

const GITLAB_URL = process.env.GITLAB_URL || 'https://gitlab.example.com';
const GITLAB_TOKEN = process.env.GITLAB_TOKEN;

/**
 * Fetch merge request diff
 */
async function fetchMrDiff(projectPath, mrIid) {
    const encodedPath = encodeURIComponent(projectPath);
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
 * Add a general comment to a merge request
 */
async function addMrGeneralComment(projectPath, mrIid, commentBody) {
    const encodedPath = encodeURIComponent(projectPath);
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
 * Main function to handle single message for testing
 */
async function main() {
    const input = await new Promise((resolve) => {
        let inputData = '';
        process.stdin.on('data', (chunk) => {
            inputData += chunk;
        });
        process.stdin.on('end', () => {
            resolve(inputData.trim());
        });
    });

    if (!input) {
        process.exit(0);
    }

    let msg;
    try {
        msg = JSON.parse(input);
    } catch (error) {
        respond({ type: 'error', message: 'Invalid JSON' });
        process.exit(1);
    }

    const msgType = msg.type;

    try {
        if (msgType === 'initialize') {
            respond({
                type: 'initialize_result',
                protocol_version: '0.1',
                server_info: { name: 'Private GitLab MCP', version: '0.1.0' }
            });
        } else if (msgType === 'tools/list') {
            respond({
                type: 'tools/list_result',
                tools: [
                    {
                        name: 'hello_world',
                        description: 'Returns a friendly hello message',
                        input_schema: {
                            type: 'object',
                            properties: {},
                            required: []
                        }
                    },
                    {
                        name: 'fetch_merge_request_diff',
                        description: 'Fetches the diff of a given merge request for a GitLab project',
                        input_schema: {
                            type: 'object',
                            properties: {
                                project_path: { type: 'string' },
                                mr_iid: { type: 'integer' }
                            },
                            required: ['project_path', 'mr_iid']
                        }
                    },
                    {
                        name: 'add_merge_request_general_comment',
                        description: 'Adds a general comment to a merge request (appears in Overview tab)',
                        input_schema: {
                            type: 'object',
                            properties: {
                                project_path: { type: 'string' },
                                mr_iid: { type: 'integer' },
                                comment_body: { type: 'string' }
                            },
                            required: ['project_path', 'mr_iid', 'comment_body']
                        }
                    }
                ]
            });
        } else if (msgType === 'tools/call') {
            const toolName = msg.name;
            const params = msg.params || {};

            if (toolName === 'hello_world') {
                respond({
                    type: 'tools/call_result',
                    result: 'Hello from your Private GitLab MCP!'
                });
            } else if (toolName === 'fetch_merge_request_diff') {
                const projectPath = params.project_path || 'your-group/your-project';
                const mrIid = params.mr_iid;
                const result = await fetchMrDiff(projectPath, mrIid);
                respond({
                    type: 'tools/call_result',
                    result: result
                });
            } else if (toolName === 'add_merge_request_general_comment') {
                const { project_path, mr_iid, comment_body } = params;
                
                if (!project_path || !mr_iid || !comment_body) {
                    throw new Error('Missing required parameters: project_path, mr_iid, and comment_body');
                }
                
                const result = await addMrGeneralComment(project_path, mr_iid, comment_body);
                respond({
                    type: 'tools/call_result',
                    result: `Successfully added general comment to merge request ${mr_iid}. Note ID: ${result.id}`
                });
            } else {
                throw new Error(`Unknown tool: ${toolName}`);
            }
        } else {
            respond({ type: 'error', message: `Unknown message type: ${msgType}` });
        }
    } catch (error) {
        respond({ type: 'error', message: error.message });
    }

    // Exit after processing one message (for testing)
    process.exit(0);
}

if (require.main === module) {
    main().catch(error => {
        console.error('Test server error:', error);
        process.exit(1);
    });
}

module.exports = {
    fetchMrDiff,
    addMrGeneralComment,
    main
};