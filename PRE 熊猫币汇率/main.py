import random


class CurrencyExchangeSimulator:
    def __init__(self):
        self.a_b_rate = 20.0
        self.b_c_rate = 10.0

        self.a_b_bounds = (15.0, 25.0)
        self.b_c_bounds = (9.5, 10.5)

        self.alpha = 0.1
        self.beta = 0.001
        self.gamma = 0.05

        self.interventions = []
        self.arbitrage_events = 0

    def get_cross_rate(self):
        """计算交叉汇率A/C"""
        return self.a_b_rate * self.b_c_rate

    def adjust_rate(self, current_rate, demand, supply, bounds, alpha, beta):
        """通用汇率调整算法"""
        # 计算供需影响
        demand_supply_ratio = (demand - supply) / (demand + supply + 1e-6)
        adjustment = alpha * demand_supply_ratio

        # 添加随机扰动
        perturbation = beta * random.uniform(-2.0, 2.0)

        # 计算新汇率
        new_rate = current_rate * (1 + adjustment + perturbation)

        # 央行干预
        if new_rate > bounds[1]:
            new_rate = bounds[1]
            self.interventions.append(
                f"干预：{current_rate:.2f}→{new_rate:.2f} 触及上限")
        elif new_rate < bounds[0]:
            new_rate = bounds[0]
            self.interventions.append(
                f"干预：{current_rate:.2f}→{new_rate:.2f} 触及下限")

        return new_rate

    def check_arbitrage(self):
        """检查套利机会并强制修正"""
        cross_rate = self.get_cross_rate()
        direct_rate = self.a_b_rate * self.b_c_rate  # 假设存在直接报价

        if abs(cross_rate - direct_rate) > 1e-2:
            self.arbitrage_events += 1
            # 简单修正：向交叉汇率方向调整50%
            self.a_b_rate = (self.a_b_rate + cross_rate/self.b_c_rate) / 2
            self.b_c_rate = (self.b_c_rate + cross_rate/self.a_b_rate) / 2
            return True
        return False

    def simulate_day(self):
        """模拟单日汇率变动"""
        # 生成市场数据
        a_demand = random.randint(80, 120)
        a_supply = random.randint(80, 120)
        b_demand = random.randint(80, 120)
        b_supply = random.randint(80, 120)

        # 调整A/B汇率
        new_a_b = self.adjust_rate(
            self.a_b_rate,
            a_demand,
            a_supply,
            self.a_b_bounds,
            self.alpha,
            self.beta
        )

        # 调整B/C汇率（使用不同参数）
        new_b_c = self.adjust_rate(
            self.b_c_rate,
            b_demand,
            b_supply,
            self.b_c_bounds,
            self.alpha*0.8,
            self.beta*0.5
        )

        # 应用调整
        self.a_b_rate, self.b_c_rate = new_a_b, new_b_c

        # 检查交叉汇率一致性
        self.check_arbitrage()

        # 返回当日汇率快照
        return {
            'A/B': round(self.a_b_rate, 4),
            'B/C': round(self.b_c_rate, 4),
            'A/C': round(self.get_cross_rate(), 4)
        }

    def run_simulation(self, days=10):
        """运行模拟"""
        history = []
        with open('out.txt','a') as f:
            f.write(f"{'Day':<5}{'A/B':<10}{'B/C':<10}{'A/C':<10}\n")
            f.write('-'*35)
            f.write("\n")
        print(f"{'Day':<5}{'A/B':<10}{'B/C':<10}{'A/C':<10}")
        print("-" * 35)

        for day in range(1, days+1):
            snapshot = self.simulate_day()
            history.append(snapshot)
            with open('out.txt',mode='a',encoding="UTF-8") as f:
                b = f"{day:<5}{snapshot['A/B']:<10.4f}"f"{snapshot['B/C']:<10.4f}{snapshot['A/C']:<10.4f}\n"
                f.write(b)
            print(f"{day:<5}{snapshot['A/B']:<10.4f}"
                  f"{snapshot['B/C']:<10.4f}{snapshot['A/C']:<10.4f}")
        # 输出统计报告
        print("\n模拟统计:")
        print(f"总干预次数: {len(self.interventions)}次")
        print(f"套利事件: {self.arbitrage_events}次")
        if self.interventions:
            print("\n最近干预记录:")
            for i in self.interventions[-10:]:
                print(f"- {i}")


# 运行模拟
if __name__ == "__main__":
    with open('out.txt','w') as f:
        f.write("")
    simulator = CurrencyExchangeSimulator()
    simulator.run_simulation(days=30)