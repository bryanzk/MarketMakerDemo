/**
 * API Call Diagnostics Helper / API 调用诊断辅助工具
 * 
 * Wraps all fetch calls to log: URL, status, latency, payload, and errors.
 * 包装所有 fetch 调用以记录：URL、状态、延迟、负载和错误。
 */

class ApiDiagnostics {
    constructor(maxCalls = 50) {
        this.calls = [];
        this.maxCalls = maxCalls;
    }
    
    /**
     * Wrap fetch call with diagnostics / 用诊断包装 fetch 调用
     * @param {string} url - API endpoint URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>}
     */
    async fetch(url, options = {}) {
        const startTime = performance.now();
        const callId = `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Hash payload for logging (without secrets) / 为日志记录哈希负载（不含密钥）
        const payloadHash = options.body 
            ? this.hashPayload(options.body) 
            : null;
        
        try {
            const response = await window.fetch(url, options);
            const latency = performance.now() - startTime;
            
            // Clone response for reading body / 克隆响应以读取正文
            const clonedResponse = response.clone();
            let parsedPayload = null;
            
            try {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    parsedPayload = await clonedResponse.json();
                }
            } catch (e) {
                // Ignore parse errors / 忽略解析错误
            }
            
            // Record call / 记录调用
            this.recordCall({
                id: callId,
                url,
                method: options.method || "GET",
                status: response.status,
                statusText: response.statusText,
                latency: Math.round(latency),
                payloadHash,
                payload: parsedPayload,
                timestamp: Date.now(),
                traceId: response.headers.get("X-Trace-ID"),
                error: parsedPayload?.error || null,
            });
            
            return response;
        } catch (error) {
            const latency = performance.now() - startTime;
            
            // Record failed call / 记录失败的调用
            this.recordCall({
                id: callId,
                url,
                method: options.method || "GET",
                status: 0,
                statusText: "Network Error",
                latency: Math.round(latency),
                payloadHash,
                payload: null,
                timestamp: Date.now(),
                traceId: null,
                error: error.message,
            });
            
            throw error;
        }
    }
    
    /**
     * Hash payload for logging / 为日志记录哈希负载
     * @param {string} payload - Request payload
     * @returns {string} Hash string
     */
    hashPayload(payload) {
        // Simple hash function / 简单哈希函数
        let hash = 0;
        const str = typeof payload === "string" ? payload : JSON.stringify(payload);
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer / 转换为32位整数
        }
        return Math.abs(hash).toString(36);
    }
    
    /**
     * Record API call / 记录 API 调用
     * @param {Object} callData - Call data
     */
    recordCall(callData) {
        this.calls.unshift(callData); // Add to beginning / 添加到开头
        if (this.calls.length > this.maxCalls) {
            this.calls.pop(); // Remove oldest / 移除最旧的
        }
    }
    
    /**
     * Get recent calls / 获取最近的调用
     * @param {Object} filters - Filter options
     * @returns {Array} Filtered calls
     */
    getRecentCalls(filters = {}) {
        let calls = this.calls;
        
        // Filter by errors only / 仅按错误过滤
        if (filters.errorsOnly) {
            calls = calls.filter(call => call.error || call.status >= 400);
        }
        
        // Filter by endpoint / 按端点过滤
        if (filters.endpoint) {
            calls = calls.filter(call => call.url.includes(filters.endpoint));
        }
        
        // Limit results / 限制结果
        if (filters.limit) {
            calls = calls.slice(0, filters.limit);
        }
        
        return calls;
    }
    
    /**
     * Clear call history / 清除调用历史
     */
    clear() {
        this.calls = [];
    }
}

// Global instance / 全局实例
const apiDiagnostics = new ApiDiagnostics();

// Make fetch wrapper available globally / 使 fetch 包装器全局可用
window.apiDiagnostics = apiDiagnostics;

// Create wrapped fetch function / 创建包装的 fetch 函数
window.diagnosticFetch = function(url, options = {}) {
    return apiDiagnostics.fetch(url, options);
};

