from processes import DataGeneratorProcess, PlottingProcess
import multiprocessing

if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    data_generator = DataGeneratorProcess(data_queue)
    plotting_process = PlottingProcess(data_queue)

    data_generator.start()
    plotting_process.start()

    data_generator.join()
    plotting_process.join()

##
from multiprocessing import Pool


def f(x):
    return x * x


if __name__ == '__main__':
    with Pool(5) as p:
        print(p.map(f, [1, 2, 3]))
