#!/bin/bash
as_stop() {
    true
}
as_start() {
    true
}
as_restart() {
    as_stop
    sleep 0.2
    as_start
}

#ms_...

case $1 in
    start|stop|restart)
        op=$1
        shift
        until [ $# -eq 0 ]
        do
            $1_$op
            shift
        done
        ;;
    *)
        echo "
        $0 start|stop|restart [as  ms ads ats | all]
        "
        ;;
esac
