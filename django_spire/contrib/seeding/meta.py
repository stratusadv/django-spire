class SeederMetaData:
    def __init__(self) -> None:
        self.run_time = 0.0
        self.cached_seed_count = 0
        self.fresh_seed_count = 0

    @property
    def total_seed_count(self) -> int:
        return self.cached_seed_count + self.fresh_seed_count

    @property
    def speed_per_seed(self) -> float:
        return self.run_time / self.total_seed_count

    @property
    def speed_per_seed_verbose(self) -> str:
        speeds_verbose_outputs = {
            0.000001: '\033[1m\033[32mDamn ... !\033[0m',
            0.00001: '\033[1m\033[32mOh Snap!\033[0m',
            0.0001: '\033[32mHyper\033[0m',
            0.001: '\033[32mFast\033[0m',
            0.01: 'Good',
            0.02: 'Acceptable',
        }
        for speed, verbose_output in speeds_verbose_outputs.items():
            if self.speed_per_seed <= speed:
                return verbose_output

        return f'\033[31mSlow :(\n -> Recommendation ... Look into Caching and Optimizations\n -> Note {"."*13} If this is Pre-Caching, Ignore this Warning\033[0m'

    def print_overview(self) -> None:
        print(f'\n\033[4m\033[1m\033[34mSeeding Overview\033[0m')
        print(f' -> Speed ............ {self.speed_per_seed_verbose}')
        print(f' -> Run Time ......... {self.run_time:10,.2f}s')
        print(f' -> Seeds ............ {self.total_seed_count:10,}')
        print(f'    -> Cached ........ {self.cached_seed_count:10,}')
        print(f'    -> Fresh ......... {self.fresh_seed_count:10,}')
        print(f'    -> Avg Speed ..... {self.speed_per_seed:10,.8f}s')
