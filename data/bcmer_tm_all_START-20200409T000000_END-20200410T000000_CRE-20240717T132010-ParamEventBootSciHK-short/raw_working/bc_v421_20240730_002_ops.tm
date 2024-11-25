KPL/MK

Meta-kernel for BepiColombo Dataset v421 -- Operational 20240730_002
============================================================================

   This meta-kernel lists the BepiColombo Operational SPICE kernels
   that provide information for the Operational scenario.

   The kernels listed in this meta-kernel and the order in which
   they are listed are picked to provide the best data available and
   the most complete coverage for the BepiColombo Operational scenario.

   This meta-kernel was generated with the Auxiliary Data Conversion
   System version: ADCSng v4.1.9.


Usage of the Meta-kernel
---------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make use
   of this kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool". The SPICELIB
   routine FURNSH loads a kernel into the pool.

   The kernels listed below can be obtained from the ESA SPICE Web server:

      https://spiftp.esac.esa.int/data/SPICE/BEPICOLOMBO/kernels/

   or from the ESA SPICE FTP server:

      ftp://spiftp.esac.esa.int/data/SPICE/BEPICOLOMBO/kernels/


Implementation Notes
---------------------------------------------------------------------------

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the BepiColombo SPICE data set's ``data'' directory on
   their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.


-------------------

   This file was created on July 30, 2024 by Alfredo Escalante Lopez ESA/ESAC.
   The original name of this file was bc_ops_v421_20240730_002.tm.


   \begindata

     PATH_VALUES       = ( '/home/kidpixo/work/esa/spice_kernels-bepicolombo/kernels' )

     PATH_SYMBOLS      = ( 'KERNELS' )

     KERNELS_TO_LOAD   = (

                           '$KERNELS/ck/bc_mpo_magboom_default_s20191107_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20181020_20190101_s20201020_v02.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20190101_20200101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20200101_20210101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20210101_20220101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20220101_20230101_s20221229_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mpo_hga_scm_20240701_20240729_s20240727_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20181020_20190101_s20200109_v02.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20190101_20200101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20200101_20210101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20210101_20220101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20220101_20230101_s20221229_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mpo_mga_scm_20240701_20240729_s20240727_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20181020_20190101_s20211202_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20190101_20200101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20200101_20210101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20210101_20220101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20220101_20230101_s20221229_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mpo_sa_scm_20240701_20240729_s20240727_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20181020_20190101_s20200109_v02.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20190101_20200101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20200101_20210101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20210101_20220101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20220101_20230101_s20221229_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mtm_sa_scm_20240701_20240729_s20240727_v01.bc'
                           '$KERNELS/ck/bc_mmo_sc_scp_20180317_20251220_f20231129_v01.bc'
                           '$KERNELS/ck/bc_mmo_sc_slt_50038_20251220_20280305_f20231129_v01.bc'
                           '$KERNELS/ck/bc_mtm_sc_scp_20180317_20251219_f20181121_v02.bc'
                           '$KERNELS/ck/bc_mtm_sep_scp_20181019_20251205_f20181127_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_prelaunch_f20181121_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_fcp_00173_20181020_20240926_f20181127_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20181019_20190101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20190101_20200101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20200101_20210101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20210101_20220101_s20230309_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20220101_20230101_s20221229_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scc_20240701_20240729_s20240727_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20181020_20190101_s20240615_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20190101_20200101_s20240615_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20200101_20210101_s20240615_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20210101_20220101_s20240615_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20220101_20230101_s20240615_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20230101_20240101_s20240104_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240101_20240131_s20240201_v03.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240201_20240229_s20240229_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240301_20240331_s20240409_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240403_20240430_s20240506_v01.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240501_20240531_s20240530_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240601_20240630_s20240629_v02.bc'
                           '$KERNELS/ck/bc_mpo_sc_scm_20240701_20240729_s20240727_v01.bc'

                           '$KERNELS/fk/bc_mpo_v36.tf'
                           '$KERNELS/fk/bc_mtm_v12.tf'
                           '$KERNELS/fk/bc_mmo_v14.tf'
                           '$KERNELS/fk/bc_ops_v01.tf'
                           '$KERNELS/fk/bc_sci_v12.tf'
                           '$KERNELS/fk/bc_dsk_surfaces_v03.tf'
                           '$KERNELS/fk/rssd0004.tf'
                           '$KERNELS/fk/earth_topo_201023.tf'
                           '$KERNELS/fk/earthstns_jaxa_20230905.tf'
                           '$KERNELS/fk/earthfixeditrf93.tf'
                           '$KERNELS/fk/estrack_v04.tf'

                           '$KERNELS/dsk/bc_mmo_sc_bus_v02.bds'
                           '$KERNELS/dsk/bc_mpo_sc_bus_v02.bds'
                           '$KERNELS/dsk/bc_mpo_sc_hga_v02.bds'
                           '$KERNELS/dsk/bc_mpo_sc_mga_v02.bds'
                           '$KERNELS/dsk/bc_mpo_sc_mosif_v02.bds'
                           '$KERNELS/dsk/bc_mpo_sc_sa_v02.bds'
                           '$KERNELS/dsk/bc_mtm_sc_bus_v02.bds'
                           '$KERNELS/dsk/bc_mtm_sc_samx_v02.bds'
                           '$KERNELS/dsk/bc_mtm_sc_sapx_v02.bds'
                           '$KERNELS/dsk/mercury_m002_mes_v02.bds'

                           '$KERNELS/ik/bc_mpo_bela_v09.ti'
                           '$KERNELS/ik/bc_mpo_mertis_v08.ti'
                           '$KERNELS/ik/bc_mpo_mgns_v03.ti'
                           '$KERNELS/ik/bc_mpo_mixs_v06.ti'
                           '$KERNELS/ik/bc_mpo_phebus_v06.ti'
                           '$KERNELS/ik/bc_mpo_serena_v09.ti'
                           '$KERNELS/ik/bc_mpo_simbio-sys_v11.ti'
                           '$KERNELS/ik/bc_mpo_sixs_v10.ti'
                           '$KERNELS/ik/bc_mpo_str_v02.ti'
                           '$KERNELS/ik/bc_mpo_aux_v01.ti'
                           '$KERNELS/ik/bc_mtm_mcam_v05.ti'
                           '$KERNELS/ik/bc_mmo_mppe_v04.ti'
                           '$KERNELS/ik/bc_mmo_msasi_v03.ti'
                           '$KERNELS/ik/bc_mmo_ssas_v01.ti'

                           '$KERNELS/lsk/naif0012.tls'

                           '$KERNELS/pck/de403_masses.tpc'
                           '$KERNELS/pck/gm_de431.tpc'
                           '$KERNELS/pck/pck00011_bc_v00.tpc'

                           '$KERNELS/pck/earth_070425_370426_predict.bpc'
                           '$KERNELS/pck/earth_000101_241022_240729.bpc'

                           '$KERNELS/sclk/bc_mpo_step_20240727.tsc'
                           '$KERNELS/sclk/bc_mpo_fict_20181127.tsc'
                           '$KERNELS/sclk/bc_mmo_step_20240103.tsc'
                           '$KERNELS/sclk/bc_mmo_fict_20231129.tsc'

                           '$KERNELS/spk/de432s.bsp'
                           '$KERNELS/spk/earthstns_itrf93_201023.bsp'
                           '$KERNELS/spk/earthstns_jaxa_20230905.bsp'
                           '$KERNELS/spk/estrack_v04.bsp'
                           '$KERNELS/spk/bc_sci_v02.bsp'
                           '$KERNELS/spk/bc_mmo_struct_v01.bsp'
                           '$KERNELS/spk/bc_mmo_scp_20181019_20251220_v02.bsp'
                           '$KERNELS/spk/bc_mtm_struct_v06.bsp'
                           '$KERNELS/spk/bc_mtm_scp_20181019_20251016_v01.bsp'
                           '$KERNELS/spk/bc_mpo_cog_v03.bsp'
                           '$KERNELS/spk/bc_mpo_cog_00173_20181118_20240804_v01.bsp'
                           '$KERNELS/spk/bc_mpo_struct_v09.bsp'
                           '$KERNELS/spk/bc_mpo_schulte_vector_v01.bsp'
                           '$KERNELS/spk/bc_mpo_prelaunch_v01.bsp'
                           '$KERNELS/spk/bc_mpo_fcp_00173_20181020_20260327_v01.bsp'

                         )

   \begintext


SPICE Kernel Dataset Version
--------------------------------------------------------------------------

   The SPICE Kernel Dataset version of the kernels present in this
   meta-kernel is provided by the following keyword (please note that
   this might not be the last version of the SPICE Kernel Dataset):

   \begindata

      SKD_VERSION = 'v421_20240730_002'

   \begintext

   The unique identifier for this meta-kernel is provided by the following
   keyword:

   \begindata

      MK_IDENTIFIER = 'bc_ops_v421_20240730_002'

   \begintext


Contact Information
--------------------------------------------------------------------------

   If you have any questions regarding this file contact the
   ESA SPICE Service (ESS) at ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           spice@sciops.esa.int,


End of MK file.