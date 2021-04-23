for i in `seq 1 50`;
do
    result="$(/opt/ncs/current/bin/ncs_cmd -c get_phase)"
    echo $result
    if [[ $result == "phase: 2"* ]]; then
        echo "phase2 complete"
        break
    fi
    sleep 5s
    time_past=$(($i*5))
    echo "$time_past seconds ..."
done

for i in `seq 1 12`;
do
    echo "show packages package package-version" | ncs_cli -u admin
    if [[ $? == 0 ]]; then
        break
    fi
    sleep 5s
    time_past=$(($i*5))
    echo "Wait $time_past seconds to connecto ncs_cli..."
done

for i in `seq 1 120`;
do
    result="$(echo 'show packages package oper-status' | ncs_cli -u admin)"
    echo $result
    if [[ $result == *"java-uninitialized"* ]]; then
        echo "Wait for Java to be initialized..."
    else
        break
    fi
    sleep 5s
    time_past=$(($i*5))
    echo "Wait $time_past seconds to check packages status..."
done
