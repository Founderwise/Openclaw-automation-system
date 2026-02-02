#!/usr/bin/env python3
"""
Founder健康监控系统
防止配置更新时"憋死"，自动检测和恢复
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests


class FounderHealthMonitor:
    """Founder健康监控器"""
    
    def __init__(self, config_path: str = None):
        # 基础路径
        self.home_dir = Path.home()
        self.openclaw_dir = self.home_dir / ".openclaw"
        self.workspace_dir = self.openclaw_dir / "workspace"
        
        # 配置文件路径
        self.config_path = config_path or str(self.openclaw_dir / "openclaw.json")
        self.config_backup_dir = self.openclaw_dir / "config_backups"
        
        # 状态文件
        self.status_file = self.workspace_dir / "founder_status.json"
        self.heartbeat_file = self.workspace_dir / "founder_heartbeat.json"
        
        # 监控配置
        self.check_interval = 300  # 5分钟检查一次
        self.timeout_threshold = 1200  # 20分钟无响应视为离线
        self.max_retries = 3
        
        # 初始化
        self._setup_directories()
        self._setup_logging()
        
        # 当前状态
        self.last_heartbeat = None
        self.consecutive_failures = 0
        self.is_monitoring = False
        
        self.logger.info("Founder健康监控系统初始化完成")
    
    def _setup_directories(self):
        """创建必要的目录"""
        self.config_backup_dir.mkdir(exist_ok=True)
        self.workspace_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self):
        """设置日志"""
        log_dir = self.workspace_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "founder_monitor.log"
        
        self.logger = logging.getLogger("FounderMonitor")
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def backup_config(self, reason: str = "manual"):
        """备份当前配置"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"openclaw_backup_{timestamp}_{reason}.json"
            backup_path = self.config_backup_dir / backup_name
            
            with open(self.config_path, 'r') as src, open(backup_path, 'w') as dst:
                config_data = json.load(src)
                # 添加备份元数据
                config_data['_backup_metadata'] = {
                    'timestamp': timestamp,
                    'reason': reason,
                    'backup_path': str(backup_path)
                }
                json.dump(config_data, dst, indent=2)
            
            self.logger.info(f"配置已备份: {backup_path}")
            
            # 清理旧备份（保留最近10个）
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置备份失败: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            backups = list(self.config_backup_dir.glob("openclaw_backup_*.json"))
            backups.sort(key=os.path.getmtime)
            
            # 保留最近10个备份
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
                    self.logger.info(f"清理旧备份: {old_backup.name}")
        except Exception as e:
            self.logger.error(f"清理备份失败: {e}")
    
    def check_openclaw_status(self) -> Tuple[bool, str]:
        """检查OpenClaw状态"""
        try:
            # 方法1: 检查进程
            result = subprocess.run(
                ["pgrep", "-f", "openclaw"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                self.logger.debug(f"找到OpenClaw进程: {pids}")
                
                # 方法2: 检查Gateway API
                try:
                    response = requests.get(
                        "http://localhost:3000/status",
                        timeout=5
                    )
                    if response.status_code == 200:
                        return True, "运行正常"
                    else:
                        return True, f"API响应异常: {response.status_code}"
                except requests.RequestException:
                    return True, "进程存在但API不可达"
            else:
                return False, "未找到运行进程"
                
        except subprocess.TimeoutExpired:
            return False, "进程检查超时"
        except Exception as e:
            self.logger.error(f"状态检查异常: {e}")
            return False, f"检查异常: {str(e)}"
    
    def send_heartbeat(self):
        """发送心跳信号"""
        heartbeat_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'alive',
            'monitor_version': '1.0.0',
            'last_action': 'heartbeat'
        }
        
        try:
            with open(self.heartbeat_file, 'w') as f:
                json.dump(heartbeat_data, f, indent=2)
            
            self.last_heartbeat = datetime.now()
            self.logger.debug("心跳信号已发送")
            
        except Exception as e:
            self.logger.error(f"发送心跳失败: {e}")
    
    def check_heartbeat_age(self) -> Optional[float]:
        """检查心跳年龄（返回秒数）"""
        try:
            if not self.heartbeat_file.exists():
                return None
            
            with open(self.heartbeat_file, 'r') as f:
                data = json.load(f)
            
            last_time = datetime.fromisoformat(data['timestamp'])
            age = (datetime.now() - last_time).total_seconds()
            
            return age
            
        except Exception as e:
            self.logger.error(f"检查心跳年龄失败: {e}")
            return None
    
    def restart_openclaw(self, force: bool = False) -> bool:
        """重启OpenClaw"""
        try:
            self.logger.info(f"开始重启OpenClaw (force={force})")
            
            # 先尝试正常停止
            if not force:
                try:
                    subprocess.run(
                        ["openclaw", "gateway", "stop"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    time.sleep(2)
                except Exception as e:
                    self.logger.warning(f"正常停止失败: {e}")
            
            # 强制停止所有相关进程
            subprocess.run(
                ["pkill", "-f", "openclaw"],
                capture_output=True,
                text=True,
                timeout=10
            )
            time.sleep(1)
            
            # 启动Gateway
            self.logger.info("启动OpenClaw Gateway...")
            
            # 在后台启动
            subprocess.Popen(
                ["openclaw", "gateway", "start"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待启动
            time.sleep(5)
            
            # 检查是否启动成功
            for i in range(10):
                is_running, message = self.check_openclaw_status()
                if is_running:
                    self.logger.info(f"OpenClaw重启成功: {message}")
                    
                    # 发送Telegram通知
                    self.send_recovery_notification()
                    
                    return True
                
                self.logger.info(f"等待启动... ({i+1}/10)")
                time.sleep(3)
            
            self.logger.error("OpenClaw启动失败")
            return False
            
        except Exception as e:
            self.logger.error(f"重启失败: {e}")
            return False
    
    def send_recovery_notification(self):
        """发送恢复通知"""
        try:
            # 这里可以集成Telegram通知
            # 暂时先记录日志
            self.logger.info("发送恢复通知")
            
            # 可以在这里调用Telegram API发送消息
            # 需要配置Telegram bot token
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
    
    def monitor_loop(self):
        """监控主循环"""
        self.is_monitoring = True
        self.logger.info("开始健康监控循环")
        
        while self.is_monitoring:
            try:
                # 发送心跳
                self.send_heartbeat()
                
                # 检查状态
                is_running, message = self.check_openclaw_status()
                
                if not is_running:
                    self.consecutive_failures += 1
                    self.logger.warning(
                        f"OpenClaw状态异常 ({self.consecutive_failures}): {message}"
                    )
                    
                    # 检查心跳年龄
                    heartbeat_age = self.check_heartbeat_age()
                    if heartbeat_age and heartbeat_age > self.timeout_threshold:
                        self.logger.error(
                            f"心跳超时 ({heartbeat_age:.0f}秒)，尝试恢复..."
                        )
                        
                        # 尝试重启
                        success = self.restart_openclaw()
                        if success:
                            self.consecutive_failures = 0
                            self.logger.info("恢复成功")
                        else:
                            self.logger.error("恢复失败")
                else:
                    if self.consecutive_failures > 0:
                        self.logger.info("状态恢复正常")
                        self.consecutive_failures = 0
                    
                    self.logger.debug(f"状态正常: {message}")
                
                # 保存状态
                self.save_status(is_running, message)
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("监控被用户中断")
                break
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                time.sleep(60)  # 异常后等待1分钟
    
    def save_status(self, is_running: bool, message: str):
        """保存状态到文件"""
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'is_running': is_running,
            'message': message,
            'consecutive_failures': self.consecutive_failures,
            'heartbeat_age': self.check_heartbeat_age(),
            'monitor_running': self.is_monitoring
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"保存状态失败: {e}")
    
    def get_status_report(self) -> Dict:
        """获取状态报告"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
            else:
                return {'error': '状态文件不存在'}
        except Exception as e:
            return {'error': f'读取状态失败: {str(e)}'}
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.logger.info("停止健康监控")


def main():
    """主函数"""
    print("=" * 60)
    print("Founder健康监控系统 v1.0.0")
    print("=" * 60)
    
    monitor = FounderHealthMonitor()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "backup":
            print("备份当前配置...")
            if monitor.backup_config("manual_backup"):
                print("✅ 配置备份成功")
            else:
                print("❌ 配置备份失败")
            return
        
        elif command == "status":
            print("检查当前状态...")
            is_running, message = monitor.check_openclaw_status()
            status = "✅ 运行正常" if is_running else "❌ 运行异常"
            print(f"状态: {status}")
            print(f"详情: {message}")
            
            # 显示状态报告
            report = monitor.get_status_report()
            print("\n状态报告:")
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return
        
        elif command == "restart":
            print("重启OpenClaw...")
            if monitor.restart_openclaw():
                print("✅ 重启成功")
            else:
                print("❌ 重启失败")
            return
        
        elif command == "test":
            print("运行测试...")
            # 测试各种功能
            monitor.backup_config("test")
            is_running, message = monitor.check_openclaw_status()
            print(f"状态检查: {is_running} - {message}")
            monitor.send_heartbeat()
            print("✅ 测试完成")
            return
    
    # 如果没有特定命令，启动监控
    print("启动健康监控系统...")
    print(f"检查间隔: {monitor.check_interval}秒")
    print(f"超时阈值: {monitor.timeout_threshold}秒")
    print(f"日志文件: {monitor.workspace_dir}/logs/founder_monitor.log")
    print(f"状态文件: {monitor.status_file}")
    print(f"心跳文件: {monitor.heartbeat_file}")
    print("\n按 Ctrl+C 停止监控")
    print("=" * 60)
    
    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n监控已停止")


if __name__ == "__main__":
    main()