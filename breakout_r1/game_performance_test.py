#!/usr/bin/env python3
"""
Breakout Game Performance Test Script for Rabbit R1 Device

This script analyzes the HTML/JavaScript game code and simulates performance
on a device with similar constraints to the Rabbit R1.

It tests:
1. Frame rate under different conditions
2. Input handling efficiency
3. Memory usage
4. CPU utilization
5. Rendering performance
"""

import os
import re
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Performance metrics to collect
metrics = {
    "fps": [],
    "cpu_usage": [],
    "memory_usage": [],
    "input_latency": [],
    "render_time": []
}

def setup_browser(throttle_cpu=True, throttle_network=False):
    """Set up browser with performance limitations similar to Rabbit R1"""
    options = Options()
    options.add_argument("--window-size=640,480")  # R1 screen resolution
    options.add_argument("--headless")  # Run headless for performance testing
    
    # Enable performance logging
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    
    # Apply CPU throttling to simulate R1's MediaTek processor
    if throttle_cpu:
        driver.execute_cdp_cmd("Emulation.setCPUThrottlingRate", {"rate": 4})  # 4x slowdown
    
    # Apply network throttling if needed
    if throttle_network:
        driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
            "offline": False,
            "latency": 100,  # ms
            "downloadThroughput": 1.5 * 1024 * 1024 / 8,  # 1.5 Mbps
            "uploadThroughput": 750 * 1024 / 8,  # 750 Kbps
        })
    
    return driver

def inject_performance_monitoring(driver):
    """Inject JavaScript to monitor game performance"""
    monitoring_script = """
    // FPS monitoring
    window.fps_samples = [];
    window.lastFrameTime = performance.now();
    window.frameCount = 0;
    
    // Override requestAnimationFrame to measure FPS
    const originalRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = function(callback) {
        return originalRAF(function(timestamp) {
            const now = performance.now();
            const elapsed = now - window.lastFrameTime;
            if (elapsed > 1000) {
                const fps = Math.round((window.frameCount * 1000) / elapsed);
                window.fps_samples.push(fps);
                window.frameCount = 0;
                window.lastFrameTime = now;
            }
            window.frameCount++;
            callback(timestamp);
        });
    };
    
    // Render time monitoring
    window.renderTimes = [];
    const originalDrawFn = window.draw;
    if (typeof originalDrawFn === 'function') {
        window.draw = function() {
            const startTime = performance.now();
            const result = originalDrawFn.apply(this, arguments);
            const endTime = performance.now();
            window.renderTimes.push(endTime - startTime);
            return result;
        };
    }
    
    // Input latency monitoring
    window.inputLatencies = [];
    const originalKeyDownHandler = window.keyDownHandler;
    if (typeof originalKeyDownHandler === 'function') {
        window.keyDownHandler = function(e) {
            const startTime = performance.now();
            const result = originalKeyDownHandler.apply(this, arguments);
            const endTime = performance.now();
            window.inputLatencies.push(endTime - startTime);
            return result;
        };
    }
    
    // Memory usage monitoring (approximation)
    window.memoryUsage = [];
    setInterval(function() {
        if (performance.memory) {
            window.memoryUsage.push(performance.memory.usedJSHeapSize / (1024 * 1024));
        }
    }, 1000);
    """
    
    driver.execute_script(monitoring_script)

def collect_performance_data(driver):
    """Collect performance metrics from the browser"""
    # Get FPS data
    fps_data = driver.execute_script("return window.fps_samples;")
    if fps_data and len(fps_data) > 0:
        metrics["fps"] = fps_data
    
    # Get render times
    render_times = driver.execute_script("return window.renderTimes;")
    if render_times and len(render_times) > 0:
        metrics["render_time"] = render_times
    
    # Get input latency
    input_latency = driver.execute_script("return window.inputLatencies;")
    if input_latency and len(input_latency) > 0:
        metrics["input_latency"] = input_latency
    
    # Get memory usage
    memory_usage = driver.execute_script("return window.memoryUsage;")
    if memory_usage and len(memory_usage) > 0:
        metrics["memory_usage"] = memory_usage
    
    # Get CPU usage from performance logs
    cpu_usage = []
    logs = driver.get_log("performance")
    for entry in logs:
        try:
            data = json.loads(entry["message"])["message"]
            if "Metrics.TaskDuration" in data.get("method", ""):
                if "data" in data.get("params", {}) and "duration" in data["params"]["data"]:
                    cpu_usage.append(data["params"]["data"]["duration"])
        except:
            pass
    
    if cpu_usage:
        metrics["cpu_usage"] = cpu_usage

def test_scroll_wheel_input(driver):
    """Test scroll wheel input handling"""
    print("Testing scroll wheel input...")
    
    try:
        # Wait for game to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gameCanvas"))
        )
        
        # Start the game
        start_button = driver.find_element(By.ID, "startButton")
        start_button.click()
        
        # Wait for game to start
        time.sleep(1)
        
        # Simulate scroll wheel events
        canvas = driver.find_element(By.ID, "gameCanvas")
        
        # Test different scroll speeds
        scroll_speeds = [120, 240, 480]  # Delta values
        
        for speed in scroll_speeds:
            # Scroll down (move right)
            driver.execute_script("""
                var canvas = document.getElementById('gameCanvas');
                var evt = new WheelEvent('wheel', {
                    deltaY: arguments[0],
                    bubbles: true,
                    cancelable: true
                });
                canvas.dispatchEvent(evt);
            """, speed)
            time.sleep(0.5)
            
            # Scroll up (move left)
            driver.execute_script("""
                var canvas = document.getElementById('gameCanvas');
                var evt = new WheelEvent('wheel', {
                    deltaY: -arguments[0],
                    bubbles: true,
                    cancelable: true
                });
                canvas.dispatchEvent(evt);
            """, speed)
            time.sleep(0.5)
        
        # Test rapid scroll changes
        for _ in range(10):
            driver.execute_script("""
                var canvas = document.getElementById('gameCanvas');
                var evt = new WheelEvent('wheel', {
                    deltaY: arguments[0],
                    bubbles: true,
                    cancelable: true
                });
                canvas.dispatchEvent(evt);
            """, 120 * (1 if _ % 2 == 0 else -1))
            time.sleep(0.1)
        
        print("Scroll wheel input test completed")
    except Exception as e:
        print(f"Error during scroll wheel testing: {e}")

def test_keyboard_input(driver):
    """Test keyboard input handling"""
    print("Testing keyboard input...")
    
    try:
        # Wait for game to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gameCanvas"))
        )
        
        # Start the game if not started
        try:
            start_button = driver.find_element(By.ID, "startButton")
            start_button.click()
            time.sleep(1)
        except:
            pass  # Game might already be started
        
        # Get the canvas element to focus
        canvas = driver.find_element(By.ID, "gameCanvas")
        canvas.click()
        
        # Test arrow key inputs
        actions = ActionChains(driver)
        
        # Test left and right arrow keys
        for _ in range(5):
            actions.send_keys(Keys.ARROW_RIGHT)
            actions.pause(0.2)
            actions.perform()
            time.sleep(0.2)
            
            actions.send_keys(Keys.ARROW_LEFT)
            actions.pause(0.2)
            actions.perform()
            time.sleep(0.2)
        
        # Test rapid key presses
        for _ in range(10):
            key = Keys.ARROW_RIGHT if _ % 2 == 0 else Keys.ARROW_LEFT
            actions.send_keys(key)
            actions.pause(0.05)
            actions.perform()
            time.sleep(0.05)
        
        print("Keyboard input test completed")
    except Exception as e:
        print(f"Error during keyboard testing: {e}")

def analyze_game_code(html_file):
    """Analyze the game code for potential performance issues"""
    print("Analyzing game code for potential performance issues...")
    
    with open(html_file, 'r') as f:
        code = f.read()
    
    issues = []
    
    # Check for potential performance issues
    
    # 1. Check for inefficient animation loop
    if "requestAnimationFrame" not in code:
        issues.append("No requestAnimationFrame found - may be using inefficient animation method")
    
    # 2. Check for potential memory leaks (event listeners not being removed)
    event_listeners = re.findall(r'addEventListener\([\'"](\w+)[\'"]', code)
    event_removals = re.findall(r'removeEventListener\([\'"](\w+)[\'"]', code)
    
    if len(event_listeners) > len(event_removals):
        issues.append(f"Potential memory leak: {len(event_listeners)} event listeners added but only {len(event_removals)} removed")
    
    # 3. Check for inefficient DOM operations in game loop
    if re.search(r'(draw|update|render).*?(getElementById|querySelector)', code, re.DOTALL):
        issues.append("DOM queries inside game loop - consider caching DOM elements")
    
    # 4. Check for canvas clearing method
    if "clearRect" in code:
        pass  # Good practice
    elif "width = width" in code:
        issues.append("Using canvas.width = canvas.width to clear - less efficient than clearRect")
    
    # 5. Check for potential input handling issues
    if "preventDefault" not in code and ("wheel" in code or "touchmove" in code):
        issues.append("Missing preventDefault() in wheel or touch events - may cause page scrolling")
    
    # 6. Check for debouncing/throttling of input
    if ("wheel" in code or "scroll" in code) and "setTimeout" not in code and "debounce" not in code:
        issues.append("Input events may not be debounced/throttled - could cause performance issues with rapid inputs")
    
    return issues

def generate_report(metrics, code_issues):
    """Generate a performance report"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "fps": {
                "avg": sum(metrics["fps"]) / len(metrics["fps"]) if metrics["fps"] else 0,
                "min": min(metrics["fps"]) if metrics["fps"] else 0,
                "max": max(metrics["fps"]) if metrics["fps"] else 0
            },
            "render_time": {
                "avg": sum(metrics["render_time"]) / len(metrics["render_time"]) if metrics["render_time"] else 0,
                "max": max(metrics["render_time"]) if metrics["render_time"] else 0
            },
            "input_latency": {
                "avg": sum(metrics["input_latency"]) / len(metrics["input_latency"]) if metrics["input_latency"] else 0,
                "max": max(metrics["input_latency"]) if metrics["input_latency"] else 0
            },
            "memory_usage": {
                "avg": sum(metrics["memory_usage"]) / len(metrics["memory_usage"]) if metrics["memory_usage"] else 0,
                "max": max(metrics["memory_usage"]) if metrics["memory_usage"] else 0
            }
        },
        "code_issues": code_issues,
        "recommendations": []
    }
    
    # Generate recommendations based on metrics and issues
    if report["metrics"]["fps"]["avg"] < 30:
        report["recommendations"].append("FPS below target (30) - optimize rendering and game loop")
    
    if report["metrics"]["render_time"]["avg"] > 16:  # 16ms = ~60fps
        report["recommendations"].append("Render time too high - reduce drawing operations or simplify graphics")
    
    if report["metrics"]["input_latency"]["avg"] > 100:
        report["recommendations"].append("Input latency too high - optimize event handlers")
    
    if report["metrics"]["memory_usage"]["max"] > 50:  # 50MB
        report["recommendations"].append("Memory usage high - check for memory leaks or reduce object creation")
    
    # Add recommendations based on code issues
    for issue in code_issues:
        if "memory leak" in issue.lower():
            report["recommendations"].append("Fix potential memory leaks by properly removing event listeners")
        elif "dom queries" in issue.lower():
            report["recommendations"].append("Cache DOM elements outside of game loop")
        elif "debounce" in issue.lower():
            report["recommendations"].append("Implement debouncing for scroll wheel input")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Test Breakout game performance for Rabbit R1")
    parser.add_argument("--html", default="index.html", help="Path to the game HTML file")
    parser.add_argument("--output", default="performance_report.json", help="Output file for performance report")
    parser.add_argument("--no-throttle", action="store_true", help="Disable CPU throttling")
    args = parser.parse_args()
    
    # Analyze the game code
    code_issues = analyze_game_code(args.html)
    print(f"Found {len(code_issues)} potential code issues")
    for issue in code_issues:
        print(f"- {issue}")
    
    # Create a local HTTP server to serve the game
    import http.server
    import socketserver
    import threading
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    httpd = socketserver.TCPServer(("", PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print(f"Serving game at http://localhost:{PORT}")
    
    try:
        # Setup browser with R1-like constraints
        driver = setup_browser(throttle_cpu=not args.no_throttle)
        
        # Load the game
        driver.get(f"http://localhost:{PORT}/{args.html}")
        
        # Inject performance monitoring code
        inject_performance_monitoring(driver)
        
        # Test keyboard input
        test_keyboard_input(driver)
        
        # Test scroll wheel input
        test_scroll_wheel_input(driver)
        
        # Let the game run for a bit to collect metrics
        print("Collecting performance metrics...")
        time.sleep(10)
        
        # Collect performance data
        collect_performance_data(driver)
        
        # Generate report
        report = generate_report(metrics, code_issues)
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Performance report saved to {args.output}")
        
        # Print summary
        print("\nPerformance Summary:")
        print(f"Average FPS: {report['metrics']['fps']['avg']:.2f}")
        print(f"Average render time: {report['metrics']['render_time']['avg']:.2f}ms")
        print(f"Average input latency: {report['metrics']['input_latency']['avg']:.2f}ms")
        print(f"Average memory usage: {report['metrics']['memory_usage']['avg']:.2f}MB")
        
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"- {rec}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Clean up
        try:
            driver.quit()
        except:
            pass
        
        httpd.shutdown()
        print("Test completed")

if __name__ == "__main__":
    main()