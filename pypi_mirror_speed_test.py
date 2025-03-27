import requests
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple
import statistics

MIRRORS = {
    "阿里云": "https://mirrors.aliyun.com/pypi/simple",
    "华为云": "https://repo.huaweicloud.com/repository/pypi/simple",
    "腾讯云": "https://mirrors.cloud.tencent.com/pypi/simple",
    "豆瓣": "https://pypi.doubanio.com/simple",
    "清华": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "中科大": "https://pypi.mirrors.ustc.edu.cn/simple",
    "网易": "https://mirrors.163.com/pypi/simple"
}

# 用于测试的一些常用大包
TEST_PACKAGES = [
    "torch",
    "tensorflow",
    "numpy",
    "pandas",
    "scikit-learn"
]

def get_package_url(mirror: str, package: str) -> str:
    return f"{mirror}/{package}/"

def test_mirror_speed(mirror_name: str, mirror_url: str, package: str) -> Tuple[str, float]:
    try:
        start_time = time.time()
        response = requests.get(get_package_url(mirror_url, package), timeout=10)
        if response.status_code == 200:
            elapsed = time.time() - start_time
            speed = len(response.content) / elapsed / 1024  # KB/s
            return mirror_name, speed
        return mirror_name, 0
    except:
        return mirror_name, 0

def test_all_mirrors(mirrors: Dict[str, str], packages: List[str]) -> Dict[str, List[float]]:
    results = {}
    
    def test_mirror_with_package(mirror_name: str, mirror_url: str, package: str):
        if mirror_name not in results:
            results[mirror_name] = []
        name, speed = test_mirror_speed(mirror_name, mirror_url, package)
        if speed > 0:  # 只记录成功的测试
            results[name].append(speed)
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for mirror_name, mirror_url in mirrors.items():
            for package in packages:
                executor.submit(test_mirror_with_package, mirror_name, mirror_url, package)
    
    return results

def print_results(results: Dict[str, List[float]]):
    print("\n测速结果:")
    print("-" * 50)
    print(f"{'镜像源':<10} {'平均速度(KB/s)':<15} {'最大速度(KB/s)':<15} {'最小速度(KB/s)':<15}")
    print("-" * 50)
    
    # 计算平均速度并排序
    mirror_speeds = []
    for mirror_name, speeds in results.items():
        if speeds:  # 如果有成功的测试结果
            avg_speed = statistics.mean(speeds)
            max_speed = max(speeds)
            min_speed = min(speeds)
            mirror_speeds.append((mirror_name, avg_speed, max_speed, min_speed))
    
    # 按平均速度降序排序
    mirror_speeds.sort(key=lambda x: x[1], reverse=True)
    
    for mirror_name, avg_speed, max_speed, min_speed in mirror_speeds:
        print(f"{mirror_name:<10} {avg_speed:>14.2f} {max_speed:>14.2f} {min_speed:>14.2f}")

def main():
    print("开始测试PyPI镜像源速度...")
    print(f"测试包: {', '.join(TEST_PACKAGES)}")
    results = test_all_mirrors(MIRRORS, TEST_PACKAGES)
    print_results(results)
    
    # 找出最快的镜像
    best_mirror = max(results.items(), key=lambda x: statistics.mean(x[1]) if x[1] else 0)
    print("\n推荐使用的镜像源:")
    print(f"镜像源: {best_mirror[0]}")
    print(f"地址: {MIRRORS[best_mirror[0]]}")

if __name__ == "__main__":
    main() 