from f5.common import constants as const
from f5.bigip.bigip_interfaces import domain_address
from f5.bigip.bigip_interfaces import icontrol_folder

# Networking - Self-IP
from neutron.common import log


class SNAT(object):
    def __init__(self, bigip):
        self.bigip = bigip

        # add iControl interfaces if they don't exist yet
        self.bigip.icontrol.add_interfaces(
                                           ['LocalLB.SNATPool',
                                            'LocalLB.SNATTranslationAddressV2']
                                           )

        # iControl helper objects
        self.lb_snatpool = self.bigip.icontrol.LocalLB.SNATPool
        self.lb_snataddress = \
                   self.bigip.icontrol.LocalLB.SNATTranslationAddressV2

    @icontrol_folder
    @domain_address
    @log.log
    def create(self, name=None, ip_address=None,
               traffic_group=None, snat_pool_name=None,
               folder='Common'):
        if not snat_pool_name:
            snat_pool_name = folder
        if not self.exists(name=name, folder=folder):
            if not traffic_group:
                traffic_group = const.SHARED_CONFIG_DEFAULT_TRAFFIC_GROUP
            self.lb_snataddress.create([name], [ip_address], [traffic_group])
        if self.pool_exists(name=snat_pool_name, folder=folder):
            self.add_to_pool(name=name,
                             pool_name=snat_pool_name,
                             folder=folder)
            return True
        else:
            self.create_pool(name=snat_pool_name,
                             member_name=name,
                             folder=folder)
            return True
        return False

    @icontrol_folder
    def delete(self, name=None, folder='Common'):
        if self.exists(name=name, folder=folder):
            self.lb_snatpool.delete_snat_pool([name])
            return True
        else:
            return False

    @icontrol_folder
    def get_all(self, folder='Common'):
        return self.lb_snataddress.get_list()

    @icontrol_folder
    def create_pool(self, name=None, member_name=None, folder='Common'):
        string_seq = \
         self.lb_snatpool.typefactory.create('Common.StringSequence')
        string_seq_seq = \
         self.lb_snatpool.typefactory.create('Common.StringSequenceSequence')
        string_seq.values = member_name
        string_seq_seq.values = [string_seq]
        self.lb_snatpool.create_v2([name], string_seq_seq)

    @icontrol_folder
    def add_to_pool(self, name=None, member_name=None, folder='Common'):
        string_seq = \
         self.lb_snatpool.typefactory.create('Common.StringSequence')
        string_seq_seq = \
         self.lb_snatpool.typefactory.create('Common.StringSequenceSequence')
        string_seq.values = member_name
        string_seq_seq.values = [string_seq]
        self.lb_snatpool.add_member_v2([name], string_seq_seq)

    @icontrol_folder
    def pool_exists(self, name=None, folder='Common'):
        if name in self.lb_snatpool.get_list():
            return True

    @icontrol_folder
    def exists(self, name=None, folder='Common'):
        if name in self.lb_snataddress.get_list():
            return True