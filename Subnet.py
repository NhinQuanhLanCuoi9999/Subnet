import math
import ipaddress
from tabulate import tabulate
import os
import time

def get_default_prefix(ip_net):
    first_octet = int(ip_net.network_address.exploded.split('.')[0])
    if 0 <= first_octet <= 127:
        return 8
    elif 128 <= first_octet <= 191:
        return 16
    elif 192 <= first_octet <= 223:
        return 24
    return None

def calculate_and_display_subnets(ip_with_prefix, num_subnets):
    try:
        original_network = ipaddress.ip_network(ip_with_prefix, strict=False)
        current_prefix = original_network.prefixlen
        default_prefix = get_default_prefix(original_network)

        if default_prefix and current_prefix < default_prefix:
            print("\033[1;31mLỖI: BẠN HIỆN ĐANG TÍNH SAI LOGIC. CÔNG THỨC DƯỚI ĐÂY LÀ THAM KHẢO CHỨ KHÔNG ÁP DỤNG THỰC TẾ ĐƯỢC.\033[0m")

        if current_prefix not in [8, 16, 24]:
            print(f"Lỗi: Prefix không phải thuộc lớp A, B, hoặc C (8, 16, hoặc 24). Sẽ không tính subnet mask mới.")
            new_prefix = current_prefix
        else:
            y = math.ceil(math.log2(num_subnets))
            new_prefix = current_prefix + y

        x = 32 - new_prefix

        hosts_per_subnet = 2 ** x - 2
        if hosts_per_subnet < 0:
            hosts_per_subnet = 0

        jump = 2 ** x

        if current_prefix in [8, 16, 24]:
            new_subnet_mask = f"/{new_prefix}"
        else:
            new_subnet_mask = f"/{current_prefix}"

        print(f"\nBước 1: Tính x và y")
        if current_prefix in [8, 16, 24]:
            print(f"y (số bit mượn) = tìm y sao cho 2^y >= {num_subnets} | Ta có y = {y}")
        if current_prefix <= 8:
            print(f"Lớp A: x = 24 - {y if current_prefix in [8, 16, 24] else 0} = {x}")
        elif current_prefix <= 16:
            print(f"Lớp B: x = 16 - {y if current_prefix in [8, 16, 24] else 0} = {x}")
        else:
            print(f"Lớp C: x = 8 - {y if current_prefix in [8, 16, 24] else 0} = {x}")
        print(f"x (số bit còn lại): {x}")
        print(f"Số host trong một subnet = 2^x - 2 = 2^{x} - 2 = {hosts_per_subnet}")

        print(f"\nBước 2: Tính bước nhảy")
        print(f"Bước nhảy = 2^x = 2^{x} = {jump} IP")

        print(f"\nBước 3: Subnet Mask mới = SM cũ + y = {current_prefix} + {y if current_prefix in [8, 16, 24] else 0} = {new_subnet_mask}")

        subnet_data = []
        subnet_id = int(original_network.network_address)

        for i in range(num_subnets):
            network_address = ipaddress.ip_address(subnet_id)
            broadcast_address = ipaddress.ip_address(subnet_id + jump - 1)
            usable_start = ipaddress.ip_address(subnet_id + 1) if jump > 2 else "N/A"
            usable_end = ipaddress.ip_address(subnet_id + jump - 2) if jump > 2 else "N/A"

            subnet_data.append([ 
                f"{network_address}/{new_prefix}",
                str(network_address),
                str(broadcast_address),
                jump,
                hosts_per_subnet,
                f"{usable_start} - {usable_end}" if jump > 2 else "Không có IP khả dụng"
            ])
            subnet_id += jump

        headers = ["Subnet ID", "Địa chỉ mạng", "Broadcast", "Tổng số IP", "Số IP khả dụng", "Dải IP khả dụng"]
        print("\nBảng kết quả:")
        print(tabulate(subnet_data, headers=headers, tablefmt="grid"))

        input("\nNhấn ENTER để tiếp tục.")
        return True

    except ValueError as e:
        print(f"Lỗi: {e}")
        return False

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("NHẤN CTRL+C ĐỂ THOÁT")

        ip_with_prefix = input("Nhập địa chỉ IP kèm prefix (vd: 192.168.1.0/24): ").strip()

        num_subnets = input("Nhập số subnet con: ").strip()

        if not ip_with_prefix or not num_subnets:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[1;31mLỗi: Bạn chưa nhập đủ thông tin. Hãy nhập lại.\033[0m")
            time.sleep(1)
            continue

        if calculate_and_display_subnets(ip_with_prefix, int(num_subnets)):
            print("\nHoàn tất tính toán. Bạn có thể thử lại hoặc thoát.")
        else:
            print("\nCó lỗi xảy ra trong quá trình tính toán. Hãy thử lại.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nChương trình đã kết thúc.")
