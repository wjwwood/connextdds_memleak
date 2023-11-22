import argparse
import collections
import datetime
import os
import subprocess
import time

import matplotlib.pyplot as plt
import matplotlib.animation
import psutil


def main():
    pub = None
    echo = None
    log = None

    parser = argparse.ArgumentParser()
    parser.add_argument('--publish-rate', default='1')

    args = parser.parse_args()

    pub_cmd = [
        'ros2', 'topic', 'pub',
        '-r', args.publish_rate,
        '/connext/odometry',
        'nav_msgs/msg/Odometry',
    ]
    echo_cmd = [
        'ros2', 'topic', 'echo',
        '--no-daemon',
        '/connext/odometry',
        'nav_msgs/msg/Odometry',
    ]

    try:
        log = open(os.path.join(os.path.dirname(__file__), f'memory_log-{time.time()}.csv'), 'w')
        pub = subprocess.Popen(
            pub_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        echo = subprocess.Popen(
            echo_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        rmw_impl = os.environ.get('RMW_IMPLEMENTATION', 'not set')
        qos_file = os.environ.get('NDDS_QOS_PROFILES', 'not set')
        ament_prefix_path = os.environ.get('AMENT_PREFIX_PATH', 'not set')
        nddshome = os.environ.get('NDDSHOME', 'not set')

        def print_and_log(msg):
            print(msg)
            log.write(f'{msg}\n')

        print_and_log(f'# RMW_IMPLEMENTATION={rmw_impl}')
        print_and_log(f'# NDDS_QOS_PROFILES={qos_file}')
        print_and_log(f'# AMENT_PREFIX_PATH={ament_prefix_path}')
        print_and_log(f'# NDDSHOME={nddshome}')
        print_and_log(f'# {pub_cmd}')
        print_and_log(f'# {echo_cmd}')

        assert pub.pid is not None
        assert echo.pid is not None

        ps_pub = psutil.Process(pub.pid)
        ps_echo = psutil.Process(echo.pid)

        minutes_to_keep = 60
        seconds_to_keep = minutes_to_keep * 60
        samples_to_keep = seconds_to_keep * 10
        first_time = datetime.datetime.fromtimestamp(time.time())
        times = collections.deque([first_time], maxlen=samples_to_keep)
        pub_ram = collections.deque([0], maxlen=samples_to_keep)
        echo_ram = collections.deque([0], maxlen=samples_to_keep)

        plt.style.use('fivethirtyeight')
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        def render(_):
            now = time.time()
            times.append(datetime.datetime.fromtimestamp(now))
            pub_ram.append(ps_pub.memory_info()[0] / 1024 / 1024)
            echo_ram.append(ps_echo.memory_info()[0] / 1024 / 1024)
            msg = f'{now}, {pub_ram[-1]}, {echo_ram[-1]}'
            # print(msg)
            log.write(f'{msg}\n')
            ax.cla()
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
            ax.set_ylim(0, 200)
            ax.xaxis_date()
            fig.tight_layout()

        _ = matplotlib.animation.FuncAnimation(fig, render, interval=100, cache_frame_data=False)
        plt.show()
    finally:
        if pub is not None:
            pub.terminate()
        if echo is not None:
            echo.terminate()
        if log is not None:
            log.close()


if __name__ == '__main__':
    main()
