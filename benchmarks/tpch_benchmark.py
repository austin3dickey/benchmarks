import conbench.runner

from benchmarks import _benchmark


def get_valid_cases():
    result = [["query_id", "scale_factor", "format"]]
    for query_id in range(1, 23):
        for scale_factor in [0.01, 0.1, 1, 10]:
            for _format in ["native", "parquet"]:
                result.append([query_id, scale_factor, _format])
    return result


@conbench.runner.register_benchmark
class TpchBenchmark(_benchmark.BenchmarkR):
    external, r_only = True, True
    name, r_name = "tpch", "tpc_h"
    valid_cases = get_valid_cases()

    def run(self, case=None, **kwargs):
        self._set_defaults(kwargs)
        for case in self.get_cases(case, kwargs):
            tags = self.get_tags(kwargs)
            tags["engine"] = "arrow"
            tags["memory_map"] = False
            tags["query_id"] = f"TPCH-{case[0]:02d}"
            self._manually_batch(kwargs, case)
            command = self._get_r_command(kwargs, case)
            yield self.r_benchmark(command, tags, kwargs, case)

    def _set_defaults(self, options):
        options["query_id"] = int(options.get("query_id", 1))
        options["scale_factor"] = float(options.get("scale_factor", 1))
        options["format"] = options.get("format", "native")

    def _manually_batch(self, options, case):
        # manually batch so that the batch plots display
        (_, scale_factor, _format) = case
        run_id = self.conbench.get_run_id(options)
        batch_id = f"{run_id}-{scale_factor}{_format[0]}"
        self.conbench.manually_batch(batch_id)

    def _get_r_command(self, options, case):
        return (
            f"library(arrowbench); "
            f"run_one({self.r_name}, "
            f"cpu_count={self.r_cpu_count(options)}, "
            f"format='{case[2]}', "
            f"scale_factor={case[1]}, "
            f"engine='arrow', "
            f"memory_map=FALSE, "
            f"query_id={case[0]})"
        )
