#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.io as io
import nipype.interfaces.afni as afni

#Flexibly collect data from disk to feed into workflows.
io_SelectFiles = pe.Node(io.SelectFiles(templates={'subj':['001', '002']}), name='io_SelectFiles')
)
io_SelectFiles.inputs.base_directory = '/input'
io_SelectFiles.inputs.subj = ['001', '002']

#Wraps the executable command ``3dTshift``.
afni_TShift = pe.Node(interface = afni.TShift(), name='afni_TShift')

#Wraps the executable command ``3dvolreg``.
afni_Volreg = pe.Node(interface = afni.Volreg(), name='afni_Volreg')

#Wraps the executable command ``align_epi_anat.py``.
afni_AlignEpiAnatPy = pe.Node(interface = afni.AlignEpiAnatPy(), name='afni_AlignEpiAnatPy')
afni_AlignEpiAnatPy.inputs.epi_base = 0
afni_AlignEpiAnatPy.inputs.anat2epi = False
afni_AlignEpiAnatPy.inputs.epi2anat = True
afni_AlignEpiAnatPy.inputs.volreg = 'off'
afni_AlignEpiAnatPy.inputs.tshift = 'off'
afni_AlignEpiAnatPy.inputs.outputtype = 'NIFTI_GZ'

#Generic datasink module to store structured outputs
io_DataSink = pe.Node(interface = io.DataSink(), name='io_DataSink')
io_DataSink.inputs.base_directory = '/output'

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(io_SelectFiles, "bold", afni_TShift, "in_file")
analysisflow.connect(afni_TShift, "out_file", afni_Volreg, "in_file")
analysisflow.connect(afni_Volreg, "out_file", afni_AlignEpiAnatPy, "in_file")
analysisflow.connect(io_SelectFiles, "anat", afni_AlignEpiAnatPy, "anat")
analysisflow.connect(afni_AlignEpiAnatPy, "epi_al_orig", io_DataSink, "mc_bold")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
