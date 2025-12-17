#!/usr/bin/env python3
"""
CLIProxyAPI 测试脚本
用于测试代理服务的模型列表和可用性
"""

import requests
import json
from datetime import datetime

# ============ 配置 ============
API_BASE = "http://192.168.1.102:8317/v1"
API_KEY = "cliproxy-ag-b9cd9ab23f51968c1afdf8fd2b7a6e26"

# 请求头
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def get_models():
    """获取可用模型列表"""
    print_separator("获取模型列表")
    try:
        response = requests.get(f"{API_BASE}/models", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            print(f"✅ 成功获取到 {len(models)} 个模型:\n")
            
            # 按提供商分类显示
            providers = {}
            for model in models:
                model_id = model.get("id", "unknown")
                # 简单分类
                if "claude" in model_id.lower():
                    provider = "Claude (Anthropic)"
                elif "gpt" in model_id.lower() or "o1" in model_id.lower() or "o3" in model_id.lower():
                    provider = "GPT (OpenAI/Codex)"
                elif "gemini" in model_id.lower():
                    provider = "Gemini (Google)"
                elif "qwen" in model_id.lower():
                    provider = "Qwen (阿里)"
                else:
                    provider = "其他"
                
                if provider not in providers:
                    providers[provider] = []
                providers[provider].append(model_id)
            
            for provider, model_list in sorted(providers.items()):
                print(f"📦 {provider} ({len(model_list)} 个):")
                for m in sorted(model_list):
                    print(f"   - {m}")
                print()
            
            return models
        else:
            print(f"❌ 获取失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return []
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return []

def test_model(model_id, test_message="你好，请简短回复"):
    """测试单个模型是否可用"""
    print(f"\n🔄 测试模型: {model_id}")
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": test_message}
        ],
        "max_tokens": 50,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"   ✅ 成功! 回复: {content[:100]}...")
            return True, content
        else:
            error_msg = response.text[:200]
            print(f"   ❌ 失败: HTTP {response.status_code}")
            print(f"      错误: {error_msg}")
            return False, error_msg
    except requests.Timeout:
        print(f"   ⏰ 超时 (60秒)")
        return False, "timeout"
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False, str(e)

def main():
    """主函数"""
    print("\n" + "🚀" * 20)
    print("     CLIProxyAPI 测试工具")
    print("🚀" * 20)
    print(f"\n📡 API 地址: {API_BASE}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 获取模型列表
    models = get_models()
    
    if not models:
        print("\n⚠️ 无法获取模型列表，请检查服务是否正常运行")
        return
    
    # 2. 选择一些代表性模型进行测试
    print_separator("测试模型可用性")
    
    # 选择每个提供商的一个模型进行测试
    test_models = []
    model_ids = [m.get("id", "") for m in models]
    
    # 优先测试这些模型
    priority_models = [
        "claude-sonnet-4-20250514",      # Claude 最新
        "claude-3-5-sonnet-20241022",    # Claude 3.5
        "gpt-4o",                         # GPT-4o
        "o1",                             # O1
        "gemini-2.5-pro",                # Gemini
        "gemini-2.0-flash",              # Gemini Flash
    ]
    
    for pm in priority_models:
        if pm in model_ids:
            test_models.append(pm)
    
    # 如果没有匹配的，取前3个
    if not test_models and models:
        test_models = [m.get("id") for m in models[:3]]
    
    print(f"将测试以下 {len(test_models)} 个模型:\n")
    for m in test_models:
        print(f"  • {m}")
    
    # 执行测试
    results = {}
    for model_id in test_models:
        success, response = test_model(model_id)
        results[model_id] = {"success": success, "response": response}
    
    # 3. 测试结果汇总
    print_separator("测试结果汇总")
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    print(f"\n📊 总计测试: {total_count} 个模型")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {total_count - success_count} 个")
    
    print("\n详细结果:")
    for model_id, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {model_id}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
