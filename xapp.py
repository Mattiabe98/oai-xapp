import xapp_sdk as ric
import time
import os
import pdb
from prometheus_client import start_http_server, Gauge, Summary
import socket


####################
#### PROMETHEUS METRICS
####################
# Create a Summary to track latencies
LATENCY_MAC = Summary('ric_mac_latency_us', 'Latency of MAC indications in microseconds')
LATENCY_RLC = Summary('ric_rlc_latency_us', 'Latency of RLC indications in microseconds')
LATENCY_PDCP = Summary('ric_pdcp_latency_us', 'Latency of PDCP indications in microseconds')
LATENCY_GTP = Summary('ric_gtp_latency_us', 'Latency of GTP indications in microseconds')

# Create Gauges for MAC metrics
MAC_DL_BER = Gauge('ric_mac_dl_ber', 'MAC DL BER', ['ue_id'])
MAC_UL_BER = Gauge('ric_mac_ul_ber', 'MAC UL BER', ['ue_id'])
MAC_BSR = Gauge('ric_mac_bsr', 'MAC BSR', ['ue_id'])
MAC_WB_CQI = Gauge('ric_mac_wb_cqi', 'MAC WB CQI', ['ue_id'])
MAC_DL_SCHED_RB = Gauge('ric_mac_dl_sched_rb', 'MAC DL Scheduled RBs', ['ue_id'])
MAC_UL_SCHED_RB = Gauge('ric_mac_ul_sched_rb', 'MAC UL Scheduled RBs', ['ue_id'])
MAC_PUSCH_SNR = Gauge('ric_mac_pusch_snr', 'MAC PUSCH SNR', ['ue_id'])
MAC_PUCCH_SNR = Gauge('ric_mac_pucch_snr', 'MAC PUCCH SNR', ['ue_id'])
MAC_DL_AGGR_PRB = Gauge('ric_mac_dl_aggr_prb', 'MAC DL Aggregated PRBs', ['ue_id'])
MAC_UL_AGGR_PRB = Gauge('ric_mac_ul_aggr_prb', 'MAC UL Aggregated PRBs', ['ue_id'])
MAC_DL_MCS1 = Gauge('ric_mac_dl_mcs1', 'MAC DL MCS1', ['ue_id'])
MAC_DL_MCS2 = Gauge('ric_mac_dl_mcs2', 'MAC DL MCS2', ['ue_id'])
MAC_UL_MCS1 = Gauge('ric_mac_ul_mcs1', 'MAC UL MCS1', ['ue_id'])
MAC_UL_MCS2 = Gauge('ric_mac_ul_mcs2', 'MAC UL MCS2', ['ue_id'])


# Create Gauges for RLC metrics
RLC_TX_RETX_PKTS = Gauge('ric_rlc_tx_retx_pkts', 'RLC PDU TX Retransmitted Packets', ['ue_id'])
RLC_TX_DROPPED_PKTS = Gauge('ric_rlc_tx_dropped_pkts', 'RLC PDU TX Dropped Packets', ['ue_id'])

# Create Gauges for PDCP metrics
PDCP_TX_BYTES = Gauge('ric_pdcp_tx_bytes', 'PDCP Total TX PDU Bytes', ['ue_id'])
PDCP_RX_BYTES = Gauge('ric_pdcp_rx_bytes', 'PDCP Total RX PDU Bytes', ['ue_id'])

# Create Gauges for GTP metrics
GTP_QFI = Gauge('ric_gtp_qfi', 'GTP QoS Flow Indicator', ['ue_id'])
GTP_TEID = Gauge('ric_gtp_teid', 'GTP gNB Tunnel Identifier', ['ue_id'])


####################
#### MAC INDICATION CALLBACK
####################

#  MACCallback class is defined and derived from C++ class mac_cb
class MACCallback(ric.mac_cb):
 # Define Python class 'constructor'
 def __init__(self):
     # Call C++ base class constructor
     ric.mac_cb.__init__(self)
 # Override C++ method: virtual void handle(swig_mac_ind_msg_t a) = 0;
 def handle(self, ind):
     # Print swig_mac_ind_msg_t
     if len(ind.ue_stats) > 0:
         for id, ue in enumerate(ind.ue_stats):
             t_now = time.time_ns() / 1000.0
             t_mac = ind.tstamp / 1.0
             t_diff = t_now - t_mac
             
             # Update Prometheus metrics
             LATENCY_MAC.observe(t_diff)
             MAC_DL_BER.labels(ue_id=id).set(ue.dl_bler)
             MAC_UL_BER.labels(ue_id=id).set(ue.ul_bler)
             MAC_BSR.labels(ue_id=id).set(ue.bsr)
             MAC_WB_CQI.labels(ue_id=id).set(ue.wb_cqi)
             MAC_DL_SCHED_RB.labels(ue_id=id).set(ue.dl_sched_rb)
             MAC_UL_SCHED_RB.labels(ue_id=id).set(ue.ul_sched_rb)
             MAC_PUSCH_SNR.labels(ue_id=id).set(ue.pusch_snr)
             MAC_PUCCH_SNR.labels(ue_id=id).set(ue.pucch_snr)
             MAC_DL_AGGR_PRB.labels(ue_id=id).set(ue.dl_aggr_prb)
             MAC_UL_AGGR_PRB.labels(ue_id=id).set(ue.ul_aggr_prb)
             MAC_DL_MCS1.labels(ue_id=id).set(ue.dl_mcs1)
             MAC_UL_MCS1.labels(ue_id=id).set(ue.ul_mcs1)
             MAC_DL_MCS2.labels(ue_id=id).set(ue.dl_mcs2)
             MAC_UL_MCS2.labels(ue_id=id).set(ue.ul_mcs2)
          
             print('MAC Indication tstamp = ' + str(t_mac) + ' latency = ' + str(t_diff) + ' μs')
             print('UE ID: ' + str(id))
             print('DL BER: ' + str(ue.dl_bler))
             print('UL BER: ' + str(ue.ul_bler))
             print('BSR: ' + str(ue.bsr))  # Example metric
             print('WB CQI: ' + str(ue.wb_cqi))  # Example metric
             print('DL SCHED RB: ' + str(ue.dl_sched_rb))
             print('UL SCHED RB: ' + str(ue.ul_sched_rb))
             print('PUSCH SNR: ' + str(ue.pusch_snr))
             print('PUCCH SNR: ' + str(ue.pucch_snr))
             print('DL AGGR PRB: ' + str(ue.dl_aggr_prb))
             print('UL AGGR PRB: ' + str(ue.ul_aggr_prb))
             print('DL MCS1: ' + str(ue.dl_mcs1))
             print('UL MCS2: ' + str(ue.ul_mcs2))
             print('---------------------------------------')
             
####################
#### RLC INDICATION CALLBACK
####################

class RLCCallback(ric.rlc_cb):
 # Define Python class 'constructor'
 def __init__(self):
     # Call C++ base class constructor
     ric.rlc_cb.__init__(self)
 # Override C++ method: virtual void handle(swig_rlc_ind_msg_t a) = 0;
 def handle(self, ind):
     # Print swig_rlc_ind_msg_t
     if len(ind.rb_stats) > 0:
         t_now = time.time_ns() / 1000.0
         t_rlc = ind.tstamp / 1.0
         t_diff = t_now - t_rlc
         
         # Update Prometheus metrics
         LATENCY_RLC.observe(t_diff)
         
         print('RLC Indication tstamp = ' + str(ind.tstamp) + ' latency = ' + str(t_diff) + ' μs')
         for id, rb in enumerate(ind.rb_stats):
             print('UE ID: ' + str(id))
             #print('RLC RNTI: ' + str(rb.rnti))
             RLC_TX_RETX_PKTS.labels(ue_id=id).set(rb.txpdu_retx_pkts)
             RLC_TX_DROPPED_PKTS.labels(ue_id=id).set(rb.txpdu_dd_pkts)
             print('RLC PDU TX retransmitted packets: ' + str(rb.txpdu_retx_pkts))  # Example metric
             print('RLC PDU TX dropped packets: ' + str(rb.txpdu_dd_pkts))  # Example metric

####################
#### PDCP INDICATION CALLBACK
####################

class PDCPCallback(ric.pdcp_cb):
 # Define Python class 'constructor'
 def __init__(self):
     # Call C++ base class constructor
     ric.pdcp_cb.__init__(self)
# Override C++ method: virtual void handle(swig_pdcp_ind_msg_t a) = 0;
 def handle(self, ind):
     # Print swig_pdcp_ind_msg_t
     if len(ind.rb_stats) > 0:
         t_now = time.time_ns() / 1000.0
         t_pdcp = ind.tstamp / 1.0
         t_diff = t_now - t_pdcp
         
         # Update Prometheus metrics
         LATENCY_PDCP.observe(t_diff)

         print('PDCP Indication tstamp = ' + str(ind.tstamp) + ' latency = ' + str(t_diff) + ' μs')
         for id, rb in enumerate(ind.rb_stats):
             print('UE ID: ' + str(id))
             #print('PDCP RNTI: ' + str(rb.rnti))
             PDCP_TX_BYTES.labels(ue_id=id).set(rb.txpdu_bytes)
             PDCP_RX_BYTES.labels(ue_id=id).set(rb.rxpdu_bytes)
             print('PDCP total PDU TX in bytes: ' + str(rb.txpdu_bytes))  # Example metric
             print('PDCP total PDU RX in bytes: ' + str(rb.rxpdu_bytes))  # Example metric

####################
#### GTP INDICATION CALLBACK
####################

# Create a callback for GTP which derived it from C++ class gtp_cb
class GTPCallback(ric.gtp_cb):
 def __init__(self):
     # Inherit C++ gtp_cb class
     ric.gtp_cb.__init__(self)
 # Create an override C++ method 
 def handle(self, ind):
     if len(ind.gtp_stats) > 0:
         t_now = time.time_ns() / 1000.0
         t_gtp = ind.tstamp / 1.0
         t_diff = t_now - t_gtp
         
         # Update Prometheus metrics
         LATENCY_GTP.observe(t_diff)

         print('GTP Indication tstamp = ' + str(ind.tstamp) + ' diff = ' + str(t_diff) + ' μs')
         for id, stat in enumerate(ind.gtp_stats):
             print('UE ID: ' + str(id))
             GTP_QFI.labels(ue_id=id).set(stat.qfi)
             GTP_TEID.labels(ue_id=id).set(stat.teidgnb)
             print('GTP QoS flow indicator: ' + str(stat.qfi))  # Example metric
             print('GTP gNB tunnel identifier: ' + str(stat.teidgnb))  # Example metric



####################
####  GENERAL 
####################

# Determine if the script is running in a docker container
def is_docker():
 path = '/proc/self/cgroup'
 return (
     os.path.exists(path) and
     any('docker' in line for line in open(path, 'r'))
 )

# Determine the host IP address
def get_host_ip():
 if is_docker():
     return socket.gethostbyname(socket.gethostname())
 else:
     return '0.0.0.0'


ric.init()

start_http_server(8000)

conn = ric.conn_e2_nodes()
assert(len(conn) > 0)
for i in range(0, len(conn)):
 print("Global E2 Node [" + str(i) + "]: PLMN MCC = " + str(conn[i].id.plmn.mcc))
 print("Global E2 Node [" + str(i) + "]: PLMN MNC = " + str(conn[i].id.plmn.mnc))

while True:
 ####################
 #### MAC INDICATION
 ####################
 
 mac_hndlr = []
 for i in range(0, len(conn)):
  mac_cb = MACCallback()
  hndlr = ric.report_mac_sm(conn[i].id, ric.Interval_ms_10, mac_cb)
  mac_hndlr.append(hndlr)     
  time.sleep(1)
 
 ####################
 #### RLC INDICATION
 ####################
 
 rlc_hndlr = []
 for i in range(0, len(conn)):
  rlc_cb = RLCCallback()
  hndlr = ric.report_rlc_sm(conn[i].id, ric.Interval_ms_10, rlc_cb)
  rlc_hndlr.append(hndlr) 
  time.sleep(1)
 
 ####################
 #### PDCP INDICATION
 ####################
 
 pdcp_hndlr = []
 for i in range(0, len(conn)):
  pdcp_cb = PDCPCallback()
  hndlr = ric.report_pdcp_sm(conn[i].id, ric.Interval_ms_10, pdcp_cb)
  pdcp_hndlr.append(hndlr) 
  time.sleep(1)
 
 ####################
 #### GTP INDICATION
 ####################
 
 gtp_hndlr = []
 for i in range(0, len(conn)):
  gtp_cb = GTPCallback()
  hndlr = ric.report_gtp_sm(conn[i].id, ric.Interval_ms_10, gtp_cb)
  gtp_hndlr.append(hndlr)
  time.sleep(1)
 
 # Start Prometheus HTTP server
 #host_ip = get_host_ip()
  # Expose metrics on port 8000
 print("Queried data, sleeping..")
 time.sleep(1)

### End
 for i in range(0, len(mac_hndlr)):
  ric.rm_report_mac_sm(mac_hndlr[i])
 
 for i in range(0, len(rlc_hndlr)):
  ric.rm_report_rlc_sm(rlc_hndlr[i])
 
 for i in range(0, len(pdcp_hndlr)):
  ric.rm_report_pdcp_sm(pdcp_hndlr[i])
 
 for i in range(0, len(gtp_hndlr)):
  ric.rm_report_gtp_sm(gtp_hndlr[i])

 time.sleep(10)


# Avoid deadlock. ToDo revise architecture 
while ric.try_stop == 0:
 time.sleep(1)

print("Test finished")
