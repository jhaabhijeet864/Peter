import { MCPTool } from "./base.js";
import { exec } from "child_process";
import fetch from "node-fetch";

export class PlaySpotifyTool implements MCPTool {
    name = "play_spotify";
    description = "Open the Spotify app and search for a specific song, artist, or album. Use this when the user asks to play a song on Spotify.";
    inputSchema = {
        type: "object" as const,
        properties: {
            query: {
                type: "string",
                description: "The song name, artist, or album to search and play on Spotify."
            }
        },
        required: ["query"]
    };

    async execute(args: { query: string }): Promise<string> {
        return new Promise((resolve) => {
            const encodedQuery = encodeURIComponent(args.query);
            const uri = `spotify:search:${encodedQuery}`;
            
            exec(`start "" "${uri}"`, (error) => {
                if (error) {
                    resolve(`Failed to open Spotify. Is the Spotify desktop app installed? Error: ${error.message}`);
                } else {
                    resolve(`Successfully opened Spotify and searched for: ${args.query}.`);
                }
            });
        });
    }
}

export class PlayYouTubeTool implements MCPTool {
    name = "play_youtube";
    description = "Search for a video on YouTube and automatically open the first result in the default browser. Use this when the user asks to play a video or song on YouTube.";
    inputSchema = {
        type: "object" as const,
        properties: {
            query: {
                type: "string",
                description: "The name of the video or song to search and play on YouTube."
            }
        },
        required: ["query"]
    };

    async execute(args: { query: string }): Promise<string> {
        try {
            const encodedQuery = encodeURIComponent(args.query);
            const searchUrl = `https://www.youtube.com/results?search_query=${encodedQuery}`;
            
            const response = await fetch(searchUrl);
            const html = await response.text();
            
            const match = html.match(/"videoId":"([^"]{11})"/);
            
            if (match && match[1]) {
                const videoId = match[1];
                const watchUrl = `https://www.youtube.com/watch?v=${videoId}`;
                
                return new Promise((resolve) => {
                    exec(`start "" "${watchUrl}"`, (error) => {
                        if (error) {
                            resolve(`Failed to open the browser for YouTube. Error: ${error.message}`);
                        } else {
                            resolve(`Successfully found and opened the YouTube video for: ${args.query}`);
                        }
                    });
                });
            } else {
                return `Could not find a video result for: ${args.query}.`;
            }
        } catch (error: any) {
            return `Error searching YouTube: ${error.message}`;
        }
    }
}
