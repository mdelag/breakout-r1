/**
 * Edge Case Test Script for Breakout Game on Rabbit R1
 * 
 * This script tests specific edge cases mentioned in the requirements:
 * 1. Rapid input changes
 * 2. Multiple simultaneous inputs
 * 3. Browser compatibility issues
 * 4. Touch vs. keyboard vs. scroll wheel input differences
 * 
 * To use: Include this script after the main game script in index.html
 * or run it in the browser console after loading the game.
 */

class BreakoutEdgeCaseTest {
    constructor() {
        this.testResults = {
            rapidInputChanges: null,
            multipleSimultaneousInputs: null,
            browserCompatibility: null,
            inputMethodDifferences: null
        };
        
        this.canvas = document.getElementById('gameCanvas');
        this.startButton = document.getElementById('startButton');
        this.gameOverlay = document.getElementById('gameOverlay');
        
        // Store original paddle position for comparison
        this.originalPaddleX = null;
    }
    
    /**
     * Run all edge case tests
     */
    async runAllTests() {
        console.log('Starting Breakout Edge Case Tests for Rabbit R1...');
        
        // Start the game if not already started
        if (!this.gameOverlay.classList.contains('hidden')) {
            this.startButton.click();
            await this.wait(1000); // Wait for game to start
        }
        
        // Store original paddle position
        this.originalPaddleX = paddleX;
        
        // Run tests
        await this.testRapidInputChanges();
        await this.testMultipleSimultaneousInputs();
        this.testBrowserCompatibility();
        await this.testInputMethodDifferences();
        
        // Display results
        this.displayResults();
    }
    
    /**
     * Test 1: Rapid input changes
     * Simulates very fast alternating left/right inputs
     */
    async testRapidInputChanges() {
        console.log('Testing rapid input changes...');
        
        // Reset paddle position
        paddleX = (GAME_WIDTH - paddleWidth) / 2;
        
        // Simulate rapid alternating key presses
        const iterations = 20;
        const delay = 50; // ms between direction changes
        
        for (let i = 0; i < iterations; i++) {
            // Alternate between left and right
            if (i % 2 === 0) {
                // Simulate right key press
                const rightEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
                document.dispatchEvent(rightEvent);
            } else {
                // Simulate left key press
                const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
                document.dispatchEvent(leftEvent);
            }
            
            await this.wait(delay);
            
            // Release keys
            const keyUpEvent = new KeyboardEvent('keyup', { 
                key: i % 2 === 0 ? 'ArrowRight' : 'ArrowLeft' 
            });
            document.dispatchEvent(keyUpEvent);
        }
        
        // Check if paddle moved smoothly (not erratically)
        // We're looking for the paddle to have moved, but not to have jumped erratically
        const paddleMoved = paddleX !== this.originalPaddleX;
        
        this.testResults.rapidInputChanges = {
            passed: paddleMoved,
            details: `Paddle ${paddleMoved ? 'responded to' : 'did not respond to'} rapid input changes`
        };
        
        console.log(`Rapid input test ${paddleMoved ? 'PASSED' : 'FAILED'}`);
        
        // Reset state
        rightPressed = false;
        leftPressed = false;
        await this.wait(500);
    }
    
    /**
     * Test 2: Multiple simultaneous inputs
     * Simulates pressing both left and right keys at the same time,
     * then adding scroll wheel input
     */
    async testMultipleSimultaneousInputs() {
        console.log('Testing multiple simultaneous inputs...');
        
        // Reset paddle position
        paddleX = (GAME_WIDTH - paddleWidth) / 2;
        const startPosition = paddleX;
        
        // Simulate pressing both left and right arrow keys
        const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
        const rightEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        
        document.dispatchEvent(leftEvent);
        document.dispatchEvent(rightEvent);
        
        await this.wait(500); // Let the game process the inputs
        
        // Record position after conflicting key presses
        const positionAfterKeys = paddleX;
        
        // Now add a scroll wheel event
        const wheelEvent = new WheelEvent('wheel', {
            deltaY: 120,
            bubbles: true,
            cancelable: true
        });
        this.canvas.dispatchEvent(wheelEvent);
        
        await this.wait(500); // Let the game process the wheel event
        
        // Record final position
        const finalPosition = paddleX;
        
        // Check if the game handled the conflicting inputs reasonably
        // Either by prioritizing one input or by canceling them out
        const keyInputsHandled = positionAfterKeys !== startPosition; // Some movement occurred
        const wheelInputHandled = finalPosition !== positionAfterKeys; // Wheel had an effect
        
        this.testResults.multipleSimultaneousInputs = {
            passed: keyInputsHandled && wheelInputHandled,
            details: `Key inputs ${keyInputsHandled ? 'were' : 'were not'} handled, ` +
                     `Wheel input ${wheelInputHandled ? 'was' : 'was not'} handled`
        };
        
        console.log(`Multiple simultaneous inputs test ${(keyInputsHandled && wheelInputHandled) ? 'PASSED' : 'FAILED'}`);
        
        // Reset state
        rightPressed = false;
        leftPressed = false;
        await this.wait(500);
    }
    
    /**
     * Test 3: Browser compatibility
     * Checks for any browser-specific issues
     */
    testBrowserCompatibility() {
        console.log('Testing browser compatibility...');
        
        // Check for browser features used by the game
        const features = {
            requestAnimationFrame: typeof window.requestAnimationFrame === 'function',
            canvas2D: !!document.createElement('canvas').getContext('2d'),
            addEventListener: typeof window.addEventListener === 'function',
            preventDefault: typeof new Event('test').preventDefault === 'function'
        };
        
        // Check for any polyfills or fallbacks in the code
        const gameCode = document.body.innerHTML;
        const hasPolyfills = gameCode.includes('polyfill') || 
                            gameCode.includes('fallback');
        
        // Check if game is using any browser-specific features
        const usingVendorPrefixes = gameCode.includes('webkit') || 
                                   gameCode.includes('moz') || 
                                   gameCode.includes('ms');
        
        // All required features must be available
        const allFeaturesAvailable = Object.values(features).every(feature => feature);
        
        this.testResults.browserCompatibility = {
            passed: allFeaturesAvailable,
            details: `Required browser features: ${allFeaturesAvailable ? 'All available' : 'Some missing'}, ` +
                     `Polyfills: ${hasPolyfills ? 'Present' : 'Not found'}, ` +
                     `Vendor prefixes: ${usingVendorPrefixes ? 'Used' : 'Not used'}`
        };
        
        console.log(`Browser compatibility test ${allFeaturesAvailable ? 'PASSED' : 'FAILED'}`);
    }
    
    /**
     * Test 4: Input method differences
     * Tests how the game responds to different input methods
     */
    async testInputMethodDifferences() {
        console.log('Testing input method differences...');
        
        // Reset paddle position
        paddleX = (GAME_WIDTH - paddleWidth) / 2;
        
        // Test 1: Keyboard input
        const keyEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        document.dispatchEvent(keyEvent);
        await this.wait(300);
        document.dispatchEvent(new KeyboardEvent('keyup', { key: 'ArrowRight' }));
        
        const keyboardPosition = paddleX;
        const keyboardMoved = keyboardPosition !== (GAME_WIDTH - paddleWidth) / 2;
        
        // Reset paddle position
        paddleX = (GAME_WIDTH - paddleWidth) / 2;
        await this.wait(300);
        
        // Test 2: Wheel input
        const wheelEvent = new WheelEvent('wheel', {
            deltaY: 120,
            bubbles: true,
            cancelable: true
        });
        this.canvas.dispatchEvent(wheelEvent);
        await this.wait(300);
        
        const wheelPosition = paddleX;
        const wheelMoved = wheelPosition !== (GAME_WIDTH - paddleWidth) / 2;
        
        // Reset paddle position
        paddleX = (GAME_WIDTH - paddleWidth) / 2;
        await this.wait(300);
        
        // Test 3: Touch input (simulated)
        const touchStartEvent = new TouchEvent('touchstart', {
            bubbles: true,
            cancelable: true,
            touches: [{
                clientX: this.canvas.getBoundingClientRect().left + GAME_WIDTH / 4,
                clientY: this.canvas.getBoundingClientRect().top + GAME_HEIGHT / 2
            }]
        });
        
        const touchMoveEvent = new TouchEvent('touchmove', {
            bubbles: true,
            cancelable: true,
            touches: [{
                clientX: this.canvas.getBoundingClientRect().left + GAME_WIDTH / 2,
                clientY: this.canvas.getBoundingClientRect().top + GAME_HEIGHT / 2
            }]
        });
        
        this.canvas.dispatchEvent(touchStartEvent);
        await this.wait(100);
        this.canvas.dispatchEvent(touchMoveEvent);
        await this.wait(300);
        
        const touchPosition = paddleX;
        const touchMoved = touchPosition !== (GAME_WIDTH - paddleWidth) / 2;
        
        // Check if all input methods worked
        const allInputsWork = keyboardMoved && wheelMoved && touchMoved;
        
        this.testResults.inputMethodDifferences = {
            passed: allInputsWork,
            details: `Keyboard: ${keyboardMoved ? 'Worked' : 'Failed'}, ` +
                     `Wheel: ${wheelMoved ? 'Worked' : 'Failed'}, ` +
                     `Touch: ${touchMoved ? 'Worked' : 'Failed'}`
        };
        
        console.log(`Input method differences test ${allInputsWork ? 'PASSED' : 'FAILED'}`);
        
        // Reset state
        rightPressed = false;
        leftPressed = false;
    }
    
    /**
     * Display test results in console
     */
    displayResults() {
        console.log('\n===== BREAKOUT EDGE CASE TEST RESULTS =====');
        
        for (const [test, result] of Object.entries(this.testResults)) {
            const status = result.passed ? 'PASSED' : 'FAILED';
            console.log(`${test}: ${status}`);
            console.log(`  ${result.details}`);
        }
        
        const allPassed = Object.values(this.testResults)
                               .every(result => result.passed);
        
        console.log('\nOverall Result: ' + (allPassed ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'));
        console.log('=======================================');
    }
    
    /**
     * Helper function to wait for a specified time
     */
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Create and run tests when this script is loaded
const edgeCaseTest = new BreakoutEdgeCaseTest();

// Add a button to run tests
const testButton = document.createElement('button');
testButton.textContent = 'Run Edge Case Tests';
testButton.style.position = 'fixed';
testButton.style.bottom = '10px';
testButton.style.right = '10px';
testButton.style.zIndex = '1000';
testButton.style.padding = '10px';
testButton.style.backgroundColor = '#FF8C00';
testButton.style.color = 'white';
testButton.style.border = 'none';
testButton.style.borderRadius = '5px';
testButton.style.cursor = 'pointer';

testButton.addEventListener('click', () => {
    edgeCaseTest.runAllTests();
});

document.body.appendChild(testButton);

console.log('Edge case test script loaded. Click the "Run Edge Case Tests" button to start tests.');