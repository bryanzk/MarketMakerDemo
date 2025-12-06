/**
 * Client-Side Validation Layer / 客户端验证层
 * 
 * Validates order parameters before submission to prevent invalid orders.
 * 在提交前验证订单参数，防止无效订单。
 */

class OrderValidator {
    constructor() {
        // Validation rules / 验证规则
        this.rules = {
            // Symbol format / 交易对格式
            symbol: {
                pattern: /^[A-Z]{2,10}\/[A-Z]{2,10}(:[A-Z]{2,10})?$/,
                message: {
                    en: "Invalid symbol format. Expected format: BASE/QUOTE or BASE/QUOTE:SETTLE",
                    zh: "无效的交易对格式。预期格式：BASE/QUOTE 或 BASE/QUOTE:SETTLE"
                }
            },
            // Quantity / 数量
            quantity: {
                min: 0.0001,
                max: 1000,
                message: {
                    en: "Quantity must be between {min} and {max}",
                    zh: "数量必须在 {min} 和 {max} 之间"
                }
            },
            // Price / 价格
            price: {
                min: 0.0001,
                max: 1000000,
                message: {
                    en: "Price must be between {min} and {max}",
                    zh: "价格必须在 {min} 和 {max} 之间"
                }
            },
            // Leverage / 杠杆
            leverage: {
                min: 1,
                max: 125,
                message: {
                    en: "Leverage must be between {min} and {max}",
                    zh: "杠杆必须在 {min} 和 {max} 之间"
                }
            },
            // Spread / 价差
            spread: {
                min: 0.01,  // 0.01%
                max: 10,    // 10%
                message: {
                    en: "Spread must be between {min}% and {max}%",
                    zh: "价差必须在 {min}% 和 {max}% 之间"
                }
            }
        };
    }

    /**
     * Validate symbol format / 验证交易对格式
     * @param {string} symbol - Trading symbol
     * @returns {Object} Validation result
     */
    validateSymbol(symbol) {
        const result = {
            valid: true,
            errors: []
        };

        if (!symbol || typeof symbol !== 'string') {
            result.valid = false;
            result.errors.push({
                field: 'symbol',
                message: {
                    en: "Symbol is required",
                    zh: "交易对是必需的"
                }
            });
            return result;
        }

        const normalized = symbol.toUpperCase().trim();
        const pattern = this.rules.symbol.pattern;

        if (!pattern.test(normalized)) {
            result.valid = false;
            result.errors.push({
                field: 'symbol',
                message: this.rules.symbol.message
            });
        }

        return result;
    }

    /**
     * Validate quantity / 验证数量
     * @param {number} quantity - Order quantity
     * @returns {Object} Validation result
     */
    validateQuantity(quantity) {
        const result = {
            valid: true,
            errors: []
        };

        if (quantity === null || quantity === undefined || quantity === '') {
            result.valid = false;
            result.errors.push({
                field: 'quantity',
                message: {
                    en: "Quantity is required",
                    zh: "数量是必需的"
                }
            });
            return result;
        }

        const num = parseFloat(quantity);

        if (isNaN(num)) {
            result.valid = false;
            result.errors.push({
                field: 'quantity',
                message: {
                    en: "Quantity must be a number",
                    zh: "数量必须是数字"
                }
            });
            return result;
        }

        if (num <= 0) {
            result.valid = false;
            result.errors.push({
                field: 'quantity',
                message: {
                    en: "Quantity must be positive",
                    zh: "数量必须为正数"
                }
            });
            return result;
        }

        const { min, max } = this.rules.quantity;
        if (num < min || num > max) {
            result.valid = false;
            const message = {
                en: this.rules.quantity.message.en.replace('{min}', min).replace('{max}', max),
                zh: this.rules.quantity.message.zh.replace('{min}', min).replace('{max}', max)
            };
            result.errors.push({
                field: 'quantity',
                message: message
            });
        }

        return result;
    }

    /**
     * Validate price / 验证价格
     * @param {number} price - Order price
     * @returns {Object} Validation result
     */
    validatePrice(price) {
        const result = {
            valid: true,
            errors: []
        };

        if (price === null || price === undefined || price === '') {
            result.valid = false;
            result.errors.push({
                field: 'price',
                message: {
                    en: "Price is required",
                    zh: "价格是必需的"
                }
            });
            return result;
        }

        const num = parseFloat(price);

        if (isNaN(num)) {
            result.valid = false;
            result.errors.push({
                field: 'price',
                message: {
                    en: "Price must be a number",
                    zh: "价格必须是数字"
                }
            });
            return result;
        }

        if (num <= 0) {
            result.valid = false;
            result.errors.push({
                field: 'price',
                message: {
                    en: "Price must be positive",
                    zh: "价格必须为正数"
                }
            });
            return result;
        }

        const { min, max } = this.rules.price;
        if (num < min || num > max) {
            result.valid = false;
            const message = {
                en: this.rules.price.message.en.replace('{min}', min).replace('{max}', max),
                zh: this.rules.price.message.zh.replace('{min}', min).replace('{max}', max)
            };
            result.errors.push({
                field: 'price',
                message: message
            });
        }

        return result;
    }

    /**
     * Validate leverage / 验证杠杆
     * @param {number} leverage - Leverage multiplier
     * @returns {Object} Validation result
     */
    validateLeverage(leverage) {
        const result = {
            valid: true,
            errors: []
        };

        if (leverage === null || leverage === undefined || leverage === '') {
            result.valid = false;
            result.errors.push({
                field: 'leverage',
                message: {
                    en: "Leverage is required",
                    zh: "杠杆是必需的"
                }
            });
            return result;
        }

        const num = parseInt(leverage, 10);

        if (isNaN(num)) {
            result.valid = false;
            result.errors.push({
                field: 'leverage',
                message: {
                    en: "Leverage must be an integer",
                    zh: "杠杆必须是整数"
                }
            });
            return result;
        }

        const { min, max } = this.rules.leverage;
        if (num < min || num > max) {
            result.valid = false;
            const message = {
                en: this.rules.leverage.message.en.replace('{min}', min).replace('{max}', max),
                zh: this.rules.leverage.message.zh.replace('{min}', min).replace('{max}', max)
            };
            result.errors.push({
                field: 'leverage',
                message: message
            });
        }

        return result;
    }

    /**
     * Validate spread / 验证价差
     * @param {number} spread - Spread percentage
     * @returns {Object} Validation result
     */
    validateSpread(spread) {
        const result = {
            valid: true,
            errors: []
        };

        if (spread === null || spread === undefined || spread === '') {
            result.valid = false;
            result.errors.push({
                field: 'spread',
                message: {
                    en: "Spread is required",
                    zh: "价差是必需的"
                }
            });
            return result;
        }

        const num = parseFloat(spread);

        if (isNaN(num)) {
            result.valid = false;
            result.errors.push({
                field: 'spread',
                message: {
                    en: "Spread must be a number",
                    zh: "价差必须是数字"
                }
            });
            return result;
        }

        if (num < 0) {
            result.valid = false;
            result.errors.push({
                field: 'spread',
                message: {
                    en: "Spread must be non-negative",
                    zh: "价差必须为非负数"
                }
            });
            return result;
        }

        const { min, max } = this.rules.spread;
        if (num < min || num > max) {
            result.valid = false;
            const message = {
                en: this.rules.spread.message.en.replace('{min}', min).replace('{max}', max),
                zh: this.rules.spread.message.zh.replace('{min}', min).replace('{max}', max)
            };
            result.errors.push({
                field: 'spread',
                message: message
            });
        }

        return result;
    }

    /**
     * Validate order parameters / 验证订单参数
     * @param {Object} params - Order parameters
     * @param {Object} options - Validation options
     * @returns {Object} Validation result
     */
    validateOrder(params, options = {}) {
        const result = {
            valid: true,
            errors: []
        };

        // Validate symbol if provided / 如果提供了交易对则验证
        if (params.symbol !== undefined) {
            const symbolResult = this.validateSymbol(params.symbol);
            if (!symbolResult.valid) {
                result.valid = false;
                result.errors.push(...symbolResult.errors);
            }
        }

        // Validate quantity if provided / 如果提供了数量则验证
        if (params.quantity !== undefined) {
            const quantityResult = this.validateQuantity(params.quantity);
            if (!quantityResult.valid) {
                result.valid = false;
                result.errors.push(...quantityResult.errors);
            }
        }

        // Validate price if provided / 如果提供了价格则验证
        if (params.price !== undefined) {
            const priceResult = this.validatePrice(params.price);
            if (!priceResult.valid) {
                result.valid = false;
                result.errors.push(...priceResult.errors);
            }
        }

        // Validate leverage if provided / 如果提供了杠杆则验证
        if (params.leverage !== undefined) {
            const leverageResult = this.validateLeverage(params.leverage);
            if (!leverageResult.valid) {
                result.valid = false;
                result.errors.push(...leverageResult.errors);
            }
        }

        // Validate spread if provided / 如果提供了价差则验证
        if (params.spread !== undefined) {
            const spreadResult = this.validateSpread(params.spread);
            if (!spreadResult.valid) {
                result.valid = false;
                result.errors.push(...spreadResult.errors);
            }
        }

        return result;
    }

    /**
     * Display validation errors in UI / 在 UI 中显示验证错误
     * @param {Object} validationResult - Validation result
     * @param {HTMLElement} errorBox - Element to display errors
     * @param {Object} options - Display options
     */
    displayErrors(validationResult, errorBox, options = {}) {
        if (!errorBox) return;

        if (validationResult.valid || validationResult.errors.length === 0) {
            errorBox.innerHTML = '';
            errorBox.style.display = 'none';
            return;
        }

        const lang = options.language || detectLanguage();
        const errors = validationResult.errors;

        let errorHtml = '<div class="validation-errors">';
        errorHtml += `<strong>⚠️ Validation Errors / 验证错误:</strong><ul>`;

        errors.forEach(error => {
            const message = lang === 'zh' && error.message.zh 
                ? error.message.zh 
                : error.message.en || error.message;
            errorHtml += `<li><strong>${error.field}:</strong> ${escapeHtml(message)}</li>`;
        });

        errorHtml += '</ul></div>';

        errorBox.innerHTML = errorHtml;
        errorBox.style.display = 'block';
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Clear validation errors / 清除验证错误
     * @param {HTMLElement} errorBox - Element to clear
     */
    clearErrors(errorBox) {
        if (errorBox) {
            errorBox.innerHTML = '';
            errorBox.style.display = 'none';
        }
    }
}

/**
 * Detect user language / 检测用户语言
 */
function detectLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.startsWith('zh') ? 'zh' : 'en';
}

/**
 * Escape HTML to prevent XSS / 转义 HTML 以防止 XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global validator instance / 全局验证器实例
const orderValidator = new OrderValidator();

// Make validator available globally / 使验证器全局可用
window.orderValidator = orderValidator;

// Convenience functions / 便捷函数
window.validateSymbol = (symbol) => orderValidator.validateSymbol(symbol);
window.validateQuantity = (quantity) => orderValidator.validateQuantity(quantity);
window.validatePrice = (price) => orderValidator.validatePrice(price);
window.validateLeverage = (leverage) => orderValidator.validateLeverage(leverage);
window.validateSpread = (spread) => orderValidator.validateSpread(spread);
window.validateOrder = (params, options) => orderValidator.validateOrder(params, options);
window.displayValidationErrors = (result, errorBox, options) => orderValidator.displayErrors(result, errorBox, options);
window.clearValidationErrors = (errorBox) => orderValidator.clearErrors(errorBox);

