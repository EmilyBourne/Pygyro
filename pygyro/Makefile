# Export variables to children Makefiles
export EXPORTED_VARS $(EXPORTED_VARS)

# Clear unfinished targets
.DELETE_ON_ERROR:

# Define phony targets
.PHONY: clean


#----------------------------------------------------------
# Main targets
#----------------------------------------------------------

numba:
	$(MAKE) -C splines $@
	$(MAKE) -C initialisation $@
	$(MAKE) -C advection $@

pyccel_generation:
	$(MAKE) -C splines $@
	$(MAKE) -C initialisation $@
	$(MAKE) -C advection $@

pyccel:
	$(MAKE) -C splines $@
	$(MAKE) -C initialisation $@
	$(MAKE) -C advection $@

spline_eval_funcs:
	$(MAKE) -C splines $@

initialiser_func:
	$(MAKE) -C initialisation $@

accelerated_advection_steps:
	$(MAKE) -C advection $@

clean:
	$(MAKE) -C splines $@
	$(MAKE) -C initialisation $@
	$(MAKE) -C advection $@
