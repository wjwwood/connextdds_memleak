# connextdds_memleak

Attempts to reproduce a potential memory leak when using rmw_connextdds with ROS 2.

## Running

The quickstart is to set up your environment how ever you want to test it, then run:

```
python3 ./monitor_pub_echo_mem.py
```

This will run a pair of processes to test pub/echo with `ros2 topic`.
Meanwhile monitoring the memory usage, plotting it live, and depositing the data into a csv file.

Optionally, you can adjust the publish rate with the `--publish-rate` option (Hz).

The csv log files start with `memory_log-` and can be plotted afterwards with:

```
python3 ./plot_memory_log.py <path/to/memory_log-*.csv>
```

The first few lines of the csv log file contain details about the run commented with `#`.
Afterwards, the csv takes the form of `timestamp, pub memory in MB, echo memory in MB`.

### Examples of Different Configurations

If you want to change the rmw implementation to `rmw_connextdds`:

```
RMW_IMPLEMENTATION=rmw_connextdds python3 ./monitor_pub_echo_mem.py
```

If you want to use a custom QoS XML:

```
NDDS_QOS_PROFILES=`pwd`/builtin_keep_last_reliable_large_data.xml \
RMW_IMPLEMENTATION=rmw_connextdds \
python3 ./monitor_pub_echo_mem.py
```
