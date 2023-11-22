import argparse
import csv
import datetime

import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('memory_log_file')
    parser.add_argument('--downsample-factor', default=1)

    args = parser.parse_args()

    times = []
    pub_ram = []
    echo_ram = []

    with open(args.memory_log_file, 'r') as log_file:
        reader = csv.reader(filter(lambda row: row[0] != '#', log_file))
        count = -1
        for row in reader:
            count += 1
            if count % args.downsample_factor != 0:
                continue
            times.append(datetime.datetime.fromtimestamp(float(row[0])))
            pub_ram.append(float(row[1]))
            echo_ram.append(float(row[2]))

    plt.style.use('fivethirtyeight')
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    ax.plot(times, pub_ram, label='Publisher Memory (MB)')
    ax.annotate(
        f'pub: {pub_ram[-1]}',
        (times[-1], pub_ram[-1]),
        textcoords='offset points',
        xytext=(0, 10),
        ha='center')
    ax.plot(times, echo_ram, label='Subscriber Memory (MB)')
    ax.annotate(
        f'sub: {echo_ram[-1]}',
        (times[-1], echo_ram[-1]),
        textcoords='offset points',
        xytext=(0, -20),
        ha='center')
    ax.legend(loc='lower right')
    ax.set_ylim(0, 300)
    ax.xaxis_date()
    fig.tight_layout()

    plt.show()


if __name__ == '__main__':
    main()
