import ollama from 'ollama';

/**
 * The TypeScript Agent Orchestrator (Phase 5 Hybrid Router)
 * Implements the single-turn, low-latency MCP dispatch pattern.
 */
export class PeterAgent {
    
    /**
     * Processes the intent using the dynamically selected Ollama model.
     * @param transcribedText The STT output
     * @param modelName The dynamic model selected from the System Tray (.env)
     * @param systemPrompt The strict worker persona instructions
     */
    async processIntent(transcribedText: string, modelName: string, systemPrompt: string): Promise<string> {
        console.log(`[TS Agent] Executing single-turn logic via ${modelName}...`);
        
        try {
            // In the complete implementation, we will append MCP tool schemas here.
            // If the model decides a tool is needed, it calls it here in one turn.
            // For this skeleton, we generate the strict conversational reply.
            const response = await ollama.chat({
                model: modelName,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: transcribedText }
                ],
                stream: false
            });
            
            return response.message.content;
            
        } catch (error) {
            console.error("[TS Agent Error] Failed to process intent:", error);
            return "I experienced a critical processing error.";
        }
    }
}
