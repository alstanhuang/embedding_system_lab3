from bluepy.btle import Scanner, Peripheral, DefaultDelegate
import time

class NotificationDelegate(DefaultDelegate):
    def handleNotification(self, cHandle, data):
        print(f"📢 通知: Handle={cHandle}, Data={data.hex()}")

def main():
    print("🔵 簡化版BLE CCCD演示")
    
    scanner = Scanner()
    print("🔍 掃描中...")
    devices = scanner.scan(10.0)
    
    if not devices:
        print("❌ 未發現設備")
        return
    
    for i, dev in enumerate(devices):
        if dev.connectable:
            name = dev.getValueText(9) or "Unknown"
            print(f"{i}: {name} ({dev.addr})")
    

    target_device = None
    for dev in devices:
        if dev.connectable:
            target_device = dev
            break
    
    if not target_device:
        print("❌ 無可連接設備")
        return
    

    print(f"🔗 連接到: {target_device.addr}")
    peripheral = Peripheral(target_device.addr)
    peripheral.setDelegate(NotificationDelegate())
    

    services = peripheral.getServices()
    print(f"📋 發現 {len(services)} 個服務")
    

    for service in services:
        chars = service.getCharacteristics()
        for char in chars:
            if 'NOTIFY' in char.propertiesToString():
                print(f"🎯 發現可通知特徵: {char.uuid}")
                
                # 核心：設定CCCD為0x0002
                try:
                    cccd_handle = char.getHandle() + 1
                    cccd_value = b'\x02\x00'  # 0x0002 (little-endian)
                    
                    peripheral.writeCharacteristic(cccd_handle, cccd_value)
                    print(f"✅ CCCD設定成功: 0x0002")
                    
                    # 等待通知
                    print("👂 等待通知...")
                    for _ in range(30):
                        if peripheral.waitForNotifications(1.0):
                            continue
                        print("⏰ 等待中...")
                    
                    break
                    
                except Exception as e:
                    print(f"❌ CCCD設定失敗: {e}")
    
    peripheral.disconnect()
    print("🔌 已斷開連接")

if __name__ == "__main__":
    main()
