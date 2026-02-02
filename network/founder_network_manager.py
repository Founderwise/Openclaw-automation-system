#!/usr/bin/env python3
"""
Founder智能网络管理系统
整合Claude Code的网络切换和防死机措施
"""

import os
import sys
import time
import subprocess
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FounderNetworkManager:
    """Founder智能网络管理器"""
    
    def __init__(self):
        # 代理配置
        self.proxy_config = {
            "http": "http://127.0.0.1:4780",
            "https": "http://127.0.0.1:4780",
            "socks5": "socks5://127.0.0.1:4781"
        }
        
        # 国内网站列表（直连）
        self.domestic_sites = [
            "baidu.com", "taobao.com", "qq.com", "jd.com",
            "weibo.com", "zhihu.com", "bilibili.com", "163.com",
            "sina.com.cn", "sohu.com", "360.cn", "csdn.net"
        ]
        
        # 国外网站列表（需要代理）
        self.international_sites = [
            "google.com", "github.com", "telegram.org", "openai.com",
            "claude.ai", "twitter.com", "youtube.com", "reddit.com",
            "stackoverflow.com", "medium.com", "aws.amazon.com"
        ]
        
        # 状态跟踪
        self.current_proxy_state = None  # "on", "off", "auto"
        self.last_switch_time = None
        self.network_log = []
    
    def detect_proxy_state(self) -> str:
        """检测当前代理状态"""
        try:
            # 检查环境变量
            http_proxy = os.getenv("http_proxy", "")
            https_proxy = os.getenv("https_proxy", "")
            
            if http_proxy and https_proxy:
                return "on"
            else:
                return "off"
        except:
            return "unknown"
    
    def set_proxy_on(self) -> bool:
        """启用代理"""
        try:
            print("🌐 启用代理...")
            
            # 设置环境变量
            os.environ["http_proxy"] = self.proxy_config["http"]
            os.environ["https_proxy"] = self.proxy_config["https"]
            os.environ["HTTP_PROXY"] = self.proxy_config["http"]
            os.environ["HTTPS_PROXY"] = self.proxy_config["https"]
            os.environ["all_proxy"] = self.proxy_config["socks5"]
            os.environ["ALL_PROXY"] = self.proxy_config["socks5"]
            
            self.current_proxy_state = "on"
            self.last_switch_time = datetime.now()
            
            # 记录日志
            self._log_network_event("proxy_on", "代理已启用")
            
            print(f"✅ 代理已启用: {self.proxy_config['http']}")
            return True
            
        except Exception as e:
            print(f"❌ 启用代理失败: {e}")
            self._log_network_event("proxy_on_error", str(e))
            return False
    
    def set_proxy_off(self) -> bool:
        """关闭代理"""
        try:
            print("🌐 关闭代理...")
            
            # 清除环境变量
            os.environ.pop("http_proxy", None)
            os.environ.pop("https_proxy", None)
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)
            os.environ.pop("all_proxy", None)
            os.environ.pop("ALL_PROXY", None)
            
            self.current_proxy_state = "off"
            self.last_switch_time = datetime.now()
            
            # 记录日志
            self._log_network_event("proxy_off", "代理已关闭")
            
            print("✅ 代理已关闭")
            return True
            
        except Exception as e:
            print(f"❌ 关闭代理失败: {e}")
            self._log_network_event("proxy_off_error", str(e))
            return False
    
    def smart_proxy_for_url(self, url: str) -> str:
        """智能判断URL是否需要代理"""
        import urllib.parse
        
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # 检查是否国内网站
            for domestic in self.domestic_sites:
                if domestic in domain:
                    return "off"  # 国内网站，关闭代理
            
            # 检查是否国外网站
            for international in self.international_sites:
                if international in domain:
                    return "on"  # 国外网站，启用代理
            
            # 默认根据当前状态
            return self.current_proxy_state or "auto"
            
        except:
            return "auto"
    
    def test_connection(self, url: str, timeout: int = 10) -> Tuple[bool, float]:
        """测试连接"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000, 2)  # 毫秒
            
            if response.status_code == 200:
                return True, latency
            else:
                return False, latency
                
        except Exception as e:
            return False, 0
    
    def test_domestic_connection(self) -> Dict[str, any]:
        """测试国内连接"""
        test_sites = [
            ("百度", "https://www.baidu.com"),
            ("淘宝", "https://www.taobao.com"),
            ("腾讯", "https://www.qq.com")
        ]
        
        results = []
        
        # 先确保代理关闭
        self.set_proxy_off()
        
        for name, url in test_sites:
            success, latency = self.test_connection(url)
            results.append({
                "name": name,
                "url": url,
                "success": success,
                "latency_ms": latency,
                "proxy_state": "off"
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "proxy_state": "off",
            "results": results
        }
    
    def test_international_connection(self) -> Dict[str, any]:
        """测试国际连接"""
        test_sites = [
            ("Google", "https://www.google.com"),
            ("GitHub", "https://www.github.com"),
            ("Telegram API", "https://api.telegram.org")
        ]
        
        results = []
        
        # 先确保代理开启
        self.set_proxy_on()
        
        for name, url in test_sites:
            success, latency = self.test_connection(url)
            results.append({
                "name": name,
                "url": url,
                "success": success,
                "latency_ms": latency,
                "proxy_state": "on"
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "proxy_state": "on",
            "results": results
        }
    
    def restart_openclaw(self) -> bool:
        """重启OpenClaw Gateway（防死机措施）"""
        try:
            print("🔄 重启OpenClaw Gateway...")
            
            # 杀死所有Gateway进程
            subprocess.run(["pkill", "-9", "-f", "openclaw.*gateway"], 
                         capture_output=True, timeout=10)
            
            # 等待进程停止
            time.sleep(2)
            
            # 启动新的Gateway（带代理）
            gateway_cmd = [
                "openclaw", "gateway", "--port", "18789", "--verbose"
            ]
            
            # 设置代理环境
            env = os.environ.copy()
            env["http_proxy"] = self.proxy_config["http"]
            env["https_proxy"] = self.proxy_config["https"]
            
            # 在后台启动
            process = subprocess.Popen(
                gateway_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # 等待启动
            time.sleep(5)
            
            # 检查是否成功
            if process.poll() is None:  # 进程还在运行
                print(f"✅ Gateway启动成功 (PID: {process.pid})")
                
                # 测试连接
                time.sleep(2)
                success, latency = self.test_connection("http://localhost:18789/status", 5)
                
                if success:
                    print(f"✅ Gateway服务正常 (延迟: {latency}ms)")
                    self._log_network_event("gateway_restart_success", f"PID: {process.pid}")
                    return True
                else:
                    print("⚠️ Gateway启动但服务不可达")
                    self._log_network_event("gateway_restart_warning", "服务不可达")
                    return False
            else:
                print("❌ Gateway启动失败")
                stdout, stderr = process.communicate()
                print(f"错误输出: {stderr.decode()[:200]}")
                self._log_network_event("gateway_restart_failed", stderr.decode()[:100])
                return False
                
        except Exception as e:
            print(f"❌ 重启失败: {e}")
            self._log_network_event("gateway_restart_error", str(e))
            return False
    
    def health_check(self) -> Dict[str, any]:
        """全面健康检查"""
        print("🏥 执行全面健康检查...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "proxy_state": self.detect_proxy_state(),
            "checks": []
        }
        
        # 检查1: 代理状态
        proxy_state = self.detect_proxy_state()
        results["checks"].append({
            "check": "proxy_state",
            "status": "healthy" if proxy_state in ["on", "off"] else "warning",
            "details": f"当前代理状态: {proxy_state}"
        })
        
        # 检查2: 国内连接
        domestic_test = self.test_domestic_connection()
        domestic_success = all(r["success"] for r in domestic_test["results"])
        results["checks"].append({
            "check": "domestic_connection",
            "status": "healthy" if domestic_success else "failed",
            "details": f"国内连接测试: {sum(1 for r in domestic_test['results'] if r['success'])}/{len(domestic_test['results'])} 成功"
        })
        
        # 检查3: 国际连接
        international_test = self.test_international_connection()
        international_success = all(r["success"] for r in international_test["results"])
        results["checks"].append({
            "check": "international_connection",
            "status": "healthy" if international_success else "failed",
            "details": f"国际连接测试: {sum(1 for r in international_test['results'] if r['success'])}/{len(international_test['results'])} 成功"
        })
        
        # 检查4: Gateway状态
        try:
            gateway_success, gateway_latency = self.test_connection("http://localhost:18789/status", 3)
            results["checks"].append({
                "check": "gateway_status",
                "status": "healthy" if gateway_success else "failed",
                "details": f"Gateway状态: {'运行中' if gateway_success else '不可用'} (延迟: {gateway_latency}ms)"
            })
        except:
            results["checks"].append({
                "check": "gateway_status",
                "status": "failed",
                "details": "Gateway不可用"
            })
        
        # 总结
        healthy_checks = sum(1 for check in results["checks"] if check["status"] == "healthy")
        total_checks = len(results["checks"])
        
        results["summary"] = {
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "health_percentage": round(healthy_checks / total_checks * 100, 1),
            "overall_status": "healthy" if healthy_checks == total_checks else "warning" if healthy_checks >= total_checks / 2 else "critical"
        }
        
        return results
    
    def _log_network_event(self, event_type: str, details: str):
        """记录网络事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "proxy_state": self.current_proxy_state
        }
        self.network_log.append(event)
        
        # 保持日志大小
        if len(self.network_log) > 100:
            self.network_log = self.network_log[-50:]
    
    def get_status_report(self) -> str:
        """获取状态报告"""
        health = self.health_check()
        
        report = f"# 🌐 Founder网络状态报告\n\n"
        report += f"**时间**: {health['timestamp']}\n"
        report += f"**代理状态**: {health['proxy_state']}\n\n"
        
        report += "## 📊 检查结果\n"
        for check in health["checks"]:
            emoji = "✅" if check["status"] == "healthy" else "⚠️" if check["status"] == "warning" else "❌"
            report += f"{emoji} **{check['check']}**: {check['details']}\n"
        
        report += f"\n## 🏆 总结\n"
        report += f"**健康检查**: {health['summary']['healthy_checks']}/{health['summary']['total_checks']} 通过\n"
        report += f"**健康度**: {health['summary']['health_percentage']}%\n"
        report += f"**总体状态**: {health['summary']['overall_status']}\n"
        
        return report


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Founder智能网络管理系统")
        print("用法:")
        print("  python3 founder_network_manager.py status    # 查看状态")
        print("  python3 founder_network_manager.py pon       # 启用代理")
        print("  python3 founder_network_manager.py poff      # 关闭代理")
        print("  python3 founder_network_manager.py test      # 测试连接")
        print("  python3 founder_network_manager.py restart   # 重启Gateway")
        print("  python3 founder_network_manager.py health    # 全面健康检查")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = FounderNetworkManager()
    
    if command == "status":
        state = manager.detect_proxy_state()
        print(f"🌐 当前代理状态: {state}")
        print(f"📅 最后切换时间: {manager.last_switch_time}")
        
    elif command == "pon":
        manager.set_proxy_on()
        
    elif command == "poff":
        manager.set_proxy_off()
        
    elif command == "test":
        print("测试国内连接...")
        domestic = manager.test_domestic_connection()
        for result in domestic["results"]:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}: {result['latency_ms']}ms")
        
        print("\n测试国际连接...")
        international = manager.test_international_connection()
        for result in international["results"]:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}: {result['latency_ms']}ms")
        
    elif command == "restart":
        manager.restart_openclaw()
        
    elif command == "health":
        report = manager.get_status_report()
        print(report)
        
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()