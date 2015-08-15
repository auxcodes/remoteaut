# GNU GENERAL PUBLIC LICENSE
#
# Copyright (C) 2015 remoteaut - Phill Banks - https://github.com/Phill-B/remoteaut
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
import pymqi
import CMQC
import CMQCFC
import sys, getopt

# mq object variables
cmdq_name = 'ADMIN.COMMAND.QUEUE'
initq_name = 'SYSTEM.DEFAULT.INITIATION.QUEUE'
proc_name = 'RUNAUT.PROCESS'


# functions

# function for creating queues
def create_queue(qmgr, args):
    try:
        pcf = pymqi.PCFExecute(qmgr)
        print '! - trying to create queue'
        pcf.MQCMD_CREATE_Q(args)
        print '  - queue was created'
    except pymqi.MQMIError, e:
        # need to check for other exceptions as well like queue manager not reachable
        if e.comp == CMQC.MQCC_FAILED and e.reason == CMQCFC.MQRCCF_OBJECT_ALREADY_EXISTS:
            print ' * queue already exists'
            print '  - updating queue'
            try:
                print '  ! - trying to update'
                pcf.MQCMD_CHANGE_Q(args)
                print '    - updated'
            except pymqi.MQMIError, f:
                print '  * did not update queue'
                print '  - completion code: ', f.comp
                print '  - reason code:', f.reason
            pass
        else:
            print ' * an unexpected error occured, exiting program'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            # clean up created MQ objects
            cleanup(qmgr)


def command_queue(qmgr):
    # create command queue
    queue_type = CMQC.MQQT_LOCAL
    queue_desc = 'Admin Command Queue'
    max_depth = 5000
    trig_ctrl = CMQC.MQTC_ON
    trig_type = CMQC.MQTT_EVERY

    cargs = {CMQC.MQCA_Q_NAME: cmdq_name,
             CMQC.MQIA_Q_TYPE: queue_type,
             CMQC.MQCA_Q_DESC: queue_desc,
             CMQC.MQIA_MAX_Q_DEPTH: max_depth,
             CMQC.MQIA_TRIGGER_CONTROL: trig_ctrl,
             CMQC.MQIA_TRIGGER_TYPE: trig_type,
             CMQC.MQCA_PROCESS_NAME: proc_name,
             CMQC.MQCA_INITIATION_Q_NAME: initq_name}

    create_queue(qmgr, cargs)


def create_process(qmgr, file_loc):
    # create process to initiate aut script
    app_type = CMQC.MQAT_UNIX
    proc_desc = 'Process to run AUT files'
    app_id = file_loc
    env_data = '&'

    pargs = {CMQC.MQCA_PROCESS_NAME: proc_name,
             CMQC.MQCA_PROCESS_DESC: proc_desc,
             CMQC.MQIA_APPL_TYPE: app_type,
             CMQC.MQCA_APPL_ID: app_id,
             CMQC.MQCA_ENV_DATA: env_data}
    try:
        pcf = pymqi.PCFExecute(qmgr)
        print '! - trying to create process'
        pcf.MQCMD_CREATE_PROCESS(pargs)
        print '  - process was created'
    except pymqi.MQMIError, e:
        # need to check for other exceptions as well like queue manager not reachable
        if e.comp == CMQC.MQCC_FAILED and e.reason == CMQCFC.MQRCCF_OBJECT_ALREADY_EXISTS:
            print ' * process already exists'
            print '  - updating process'
            try:
                print '  ! - trying to update'
                pcf.MQCMD_CHANGE_PROCESS(pargs)
                print '    - updated'
            except pymqi.MQMIError, f:
                print '  * did not update process'
                print '  - completion code: ', f.comp
                print '  - reason code:', f.reason
            pass
        else:
            print ' * an unexpected error occured, exiting program'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            # clean up created MQ objects
            cleanup(qmgr)


# put message to queue AUT script
def put_message(qmgr):
    out_message = '!## Process Completed ##!'
    queue = pymqi.Queue(qmgr, cmdq_name)
    queue.put(out_message)
    queue.close()


# get back AUT script output message from queue
def get_message(qmgr):
    # Message Descriptor
    md = pymqi.MD()
    # Get Message Options
    gmo = pymqi.GMO()
    gmo.Options = CMQC.MQGMO_WAIT | CMQC.MQGMO_FAIL_IF_QUIESCING
    gmo.WaitInterval = 5000  # 5 seconds

    queue = pymqi.Queue(qmgr, cmdq_name)
    message = queue.get(None, md, gmo)
    queue.close()
    # print out message
    print message
    print " "
    print "#=========================================================#"
    print "|                                                         |"
    print "|  Please check your queue Authorities to confirm scripts |"
    print "|  were run successfully.                                 |"
    print "|                                                         |"
    print "#=========================================================#"
    print " "


# clear and delete queue from qmgr
def cleanup(qmgr):
    cargs = {CMQC.MQCA_Q_NAME: cmdq_name}
    pargs = {CMQC.MQCA_PROCESS_NAME: proc_name}

    pcf = pymqi.PCFExecute(qmgr)
    # clear any messages off command queue
    pcf.MQCMD_CLEAR_Q(cargs)
    print '- clearing temp command queue'
    # remove command queue
    pcf.MQCMD_DELETE_Q(cargs)
    print '- deleting temp command queue'
    # remove process
    pcf.MQCMD_DELETE_PROCESS(pargs)
    print '- deleting temp command process'

    qmgr.disconnect()


def main(argv):
    # MQ connection Variables            
    queue_manager = ''
    channel = ''
    host = ''
    port = ''
    file_loc = ''

    try:
        opts, args = getopt.getopt(argv, "hm:c:i:p:f:", ["qmgr=", "channel=", "host=", "port=", "fileloc="])
        if not opts:
            print ' '
            print '! There are missing arguements, the required inputs are:'
            print ' '
            print '  mqaut.exe -m <queue_manager> -c <channel> -i <hostname> -p <port> -f </file/path/to/aut.AUT>'
            sys.exit(2)
    except getopt.GetoptError:
        print ' '
        print '! There are missing arguements, the required inputs are:'
        print ' '
        print '  mqaut.exe -m <queue_manager> -c <channel> -i <hostname> -p <port> -f </file/path/to/aut.AUT>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ' '
            print ' The required inputs are:'
            print ' '
            print ' mqaut.exe -m <queue_manager> -c <channel> -i <hostname> -p <port> -f </file/path/to/aut.AUT>'
            sys.exit()
        elif opt in ("-m", "--qmgr"):
            queue_manager = arg
        elif opt in ("-c", "--channel"):
            channel = arg
        elif opt in ("-i", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-f", "--fileloc"):
            file_loc = arg

    print '#---------------------------------------------------------#'
    print '#------------------ CONNECTION DETAILS -------------------#'
    print ' - Queue Manager: ', queue_manager
    print ' - Channel: ', channel
    print ' - Hostname: ', host
    print ' - Port: ', port
    print ' - File Path: ', file_loc
    print '#---------------------------------------------------------#'
    print ' '

    # connect to queue manager
    conn_info = "%s(%s)" % (host, port)
    # print ' - conn info: ', conn_info
    try:
        print '! Attempting Queue Manager Connection'
        qmgr = pymqi.connect(queue_manager, channel, conn_info)
    except pymqi.MQMIError, e:
        if e.comp == CMQC.MQCC_FAILED and e.reason == CMQC.MQRC_HOST_NOT_AVAILABLE:
            print ' !! Error in the provided connection details - hostname or port'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            sys.exit(1)
        elif e.comp == CMQC.MQCC_FAILED and e.reason == CMQC.MQRC_Q_MGR_NAME_ERROR:
            print ' !! Error in provided queue manager name'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            sys.exit(1)
        elif e.comp == CMQC.MQCC_FAILED and e.reason == CMQC.MQRC_UNKNOWN_CHANNEL_NAME:
            print ' !! Error in provided channel name'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            sys.exit(1)
        else:
            print ' * an unexpected error occured, please check your connection details'
            print '  - completion code: ', e.comp
            print '  - reason code:', e.reason
            sys.exit(1)

    # perform actions in sequence
    # create queues
    command_queue(qmgr)
    # create process
    create_process(qmgr, file_loc)
    # send initiation message
    put_message(qmgr)
    get_message(qmgr)
    # clean up created MQ objects
    cleanup(qmgr)


if __name__ == "__main__":
    main(sys.argv[1:])
