import random

class CurrencyExchangeSimulator:
    def __init__(self):
        self.rates = {
            'A/B': 20.0,
            'B/C': 10.0,
            'A/B_bounds': (15.0, 25.0),
            'B/C_bounds': (9.5, 10.5)
        }
        self.params = {
            'alpha': 0.1,
            'beta': 0.001,
            'gamma': 0.05
        }
        self.interventions = []
        self.arbitrage_events = 0

    def get_cross_rate(self):
        """计算交叉汇率A/C"""
        return self.rates['A/B'] * self.rates['B/C']

    def adjust_rate(self, current_rate, demand, supply, bounds, alpha, beta):
        """通用汇率调整算法"""
        # 计算供需影响（添加极小值防止除零）
        demand_supply_ratio = (demand - supply) / (demand + supply + 1e-12)
        adjustment = alpha * demand_supply_ratio

        # 添加随机扰动
        perturbation = beta * random.uniform(-2.0, 2.0)

        # 计算新汇率并应用边界约束
        new_rate = current_rate * (1 + adjustment + perturbation)
        lower, upper = bounds

        if new_rate > upper:
            new_rate = upper
            self._record_intervention(current_rate, new_rate, '上限')
        elif new_rate < lower:
            new_rate = lower
            self._record_intervention(current_rate, new_rate, '下限')

        return new_rate

    def _record_intervention(self, old_rate, new_rate, boundary):
        """记录央行干预事件"""
        self.interventions.append(
            f"干预：{old_rate:.2f}→{new_rate:.2f} 触及{boundary}"
        )

    def check_arbitrage(self):
        """检查套利机会并修正"""
        cross_rate = self.get_cross_rate()
        direct_rate = self.rates['A/B'] * self.rates['B/C']  # 保持原有逻辑

        if abs(cross_rate - direct_rate) > 1e-2:
            self.arbitrage_events += 1
            # 修正逻辑保持原有50%调整比例
            self.rates['A/B'] = (self.rates['A/B'] + cross_rate/self.rates['B/C']) / 2
            self.rates['B/C'] = (self.rates['B/C'] + cross_rate/self.rates['A/B']) / 2
            return True
        return False

    def simulate_day(self):
        """模拟单日汇率变动"""
        # 生成市场数据（使用字典推导式简化）
        markets = {
            'A': {'demand': random.randint(80, 120), 'supply': random.randint(80, 120)},
            'B': {'demand': random.randint(80, 120), 'supply': random.randint(80, 120)}
        }

        # 调整汇率（使用参数化配置）
        adjustments = [
            ('A/B', markets['A'], self.rates['A/B_bounds'], self.params['alpha'], self.params['beta']),
            ('B/C', markets['B'], self.rates['B/C_bounds'], self.params['alpha']*0.8, self.params['beta']*0.5)
        ]

        for rate_name, market, bounds, alpha, beta in adjustments:
            new_rate = self.adjust_rate(
                current_rate=self.rates[rate_name],
                demand=market['demand'],
                supply=market['supply'],
                bounds=bounds,
                alpha=alpha,
                beta=beta
            )
            self.rates[rate_name] = new_rate

        self.check_arbitrage()

        return {
            'A/B': round(self.rates['A/B'], 4),
            'B/C': round(self.rates['B/C'], 4),
            'A/C': round(self.get_cross_rate(), 4)
        }

    def run_simulation(self, days=10, output_file='out.txt'):
        """运行模拟（添加文件输出参数）"""
        history = []
        self._init_output_file(output_file)

        header_format = "{:<5}{:<10}{:<10}{:<10}"
        detail_format = "{day:<5}{A_B:<10.4f}{B_C:<10.4f}{A_C:<10.4f}"  # 修改点：使用下划线格式

        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(header_format.format("Day", "A/B", "B/C", "A/C") + "\n")
            f.write('-'*35 + "\n")

        print(header_format.format("Day", "A/B", "B/C", "A/C"))
        print("-"*35)

        for day in range(1, days+1):
            snapshot = self.simulate_day()
            history.append(snapshot)
            
            # 修改点：使用下划线格式化参数
            output_line = detail_format.format(
                day=day,
                A_B=snapshot['A/B'],  # 保持原始字典键
                B_C=snapshot['B/C'],
                A_C=snapshot['A/C']
            )

            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(output_line + "\n")
            print(output_line)

        # 生成统计报告
        self._print_statistics()

    def _init_output_file(self, filename):
        """安全初始化输出文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                pass
        except Exception as e:
            print(f"[警告] 无法初始化输出文件：{str(e)}")

    def _print_statistics(self):
        """输出统计报告"""
        print("\n模拟统计:")
        print(f"总干预次数: {len(self.interventions)}次")
        print(f"套利事件: {self.arbitrage_events}次")
        
        if self.interventions:
            print("\n最近干预记录:")
            for record in self.interventions[-30:]:
                print(f"- {record}")

if __name__ == "__main__":
    simulator = CurrencyExchangeSimulator()
    simulator.run_simulation(days=30)