# Project settings
PROJECT_NAME := rc-bootcamp
SRC_NAME := src
BUILD_NAME := build
PRODUCT_NAME := product

# Supported languages (see https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes)
LANGUAGES := en ja

# Supported modes (ex: exercise mode, sol: solution mode)
MODES := ex sol

# Excluded files and folders
EXCLUDED_EXTS = .pyc
EXCLUDED_DIRS = .cache result __pycache__

# List of notebook names (without .ipynb) to be converted to readable markdown/PDF files
MARKDOWNIFY := README

# List of extensions for markdownified files (.ipynb -> .md, .pdf, etc.)
MARKDOWNIFY_EXTS := md pdf

# List of files/folders in the project root to be included in the product
ROOT_TO_INCLUDE := .python-version pyproject.toml uv.lock .vscode/extensions.json LICENSE.txt

# Directories and files
PROJECT_DIR := $(realpath .)
BUILD_DIR := $(PROJECT_DIR)/$(BUILD_NAME)
PRODUCT_DIR := $(PROJECT_DIR)/$(PRODUCT_NAME)
SRC_DIR := $(PROJECT_DIR)/$(SRC_NAME)
JUPYTER_FILE := $(shell find $(SRC_DIR) -type f -name "*.ipynb" | sort)
LIBRARY_FILE := $(shell find $(SRC_DIR) -type f -name "*.py" | sort)
ROOT_FILE := $(addprefix $(PROJECT_DIR)/,$(ROOT_TO_INCLUDE))

# Continuous Integration settings
ifeq ($(CI), true)
ECHO_PREFIX := "::group::"
ECHO_SUFFIX := "::endgroup::"
endif

# Targets
.DEFAULT_GOAL := deploy

deploy : clear $(LANGUAGES)

dist : clear $(addsuffix -dist,$(LANGUAGES)) archive

mark : $(addsuffix -mark,$(LANGUAGES))

test : $(addsuffix -test,$(LANGUAGES))

test-init :
	@echo "$(ECHO_PREFIX)[test-init] check all .ipynb and .py files"
	python $(PROJECT_DIR)/tool/check_and_fix_notebook.py $(JUPYTER_FILE)
	nbqa ruff $(JUPYTER_FILE)
	ruff check $(LIBRARY_FILE)
	@echo "$(ECHO_SUFFIX)"

# Ignore suffixes for built-in rules
.SUFFIXES :

# Phony targets
.PHONY : archive beautify clear clean

archive :
	mkdir -p $(PRODUCT_DIR)
	git archive HEAD --output=$(PRODUCT_DIR)/$(PROJECT_NAME)_base.zip --format=zip

beautify :
	python $(PROJECT_DIR)/tool/check_and_fix_notebook.py $(JUPYTER_FILE) --fix
	nbqa ruff $(JUPYTER_FILE) --fix

clear :
	rm -rf $(PRODUCT_DIR)

clean : clear
	rm -rf $(BUILD_DIR)

help :
	@echo "Available make targets:"
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | grep -v "^Makefile$$" | sort -u

# Language and mode specific targets
define MACRO_LANG_MODE_TARGET
$(eval LANG_MODE := $(addprefix $(1)_,$(MODES)))
$(eval LANG_MODE_DIST := $(addsuffix -dist,$(LANG_MODE)))
$(eval LANG_MODE_MARK := $(addsuffix -mark,$(LANG_MODE)))
$(eval LANG_MODE_TEST := $(addsuffix -test,$(LANG_MODE)))

$(1) : $(LANG_MODE)

$(1)-dist : $(LANG_MODE_DIST)

$(1)-mark : $(LANG_MODE_MARK)

$(1)-test : $(LANG_MODE_TEST)

endef
$(foreach lang,$(LANGUAGES),$(eval $(call MACRO_LANG_MODE_TARGET,$(lang))))

# Language and mode specific build rules
define MACRO_LANG_MODE_BUILD
$(eval SUBDIR_NAME := $(if $(filter ex,$(2)),$(PROJECT_NAME)_$(1),$(PROJECT_NAME)_$(1)_$(2)))
$(eval PRODUCT_SUBDIR := $(PRODUCT_DIR)/$(SUBDIR_NAME))
$(eval BUILD_SUBDIR := $(BUILD_DIR)/$(SUBDIR_NAME))

$(eval LANG_EXC_JUPYTER := $(foreach name,$($(1)_exclude),-not -wholename "$(SRC_DIR)/$(name).ipynb"))
$(eval LANG_INC_JUPYTER := $(foreach name,$($(1)_include),-wholename "$(SRC_DIR)/$(name).ipynb" -o))
$(eval LANG_JUPYTER_OPT := $(LANG_EXC_JUPYTER) $(if $(findstring wholename,$(LANG_INC_JUPYTER)),-and \( $(LANG_INC_JUPYTER) -false \)))
$(eval LANG_JUPYTER_FILE := $(shell find $(SRC_DIR) -type f -name "*.ipynb" $(LANG_JUPYTER_OPT) | sort))

$(eval EXC_LIBRARY := $(foreach suf,$(EXCLUDED_EXTS),-not -name "*$(suf)") $(foreach dir,$(EXCLUDED_DIRS),-not -path "$(SRC_DIR)*/$(dir)/*"))
$(eval LANG_EXC_LIBRARY := $(foreach name,$($(1)_exclude),-not -wholename "$(SRC_DIR)/data/$(name)"))
$(eval LANG_INC_LIBRARY := $(foreach name,$($(1)_include),-wholename "$(SRC_DIR)/data/$(name)" -o))
$(eval LANG_LIBRARY_OPT :=  $(EXC_LIBRARY) $(LANG_EXC_LIBRARY) $(if $(findstring wholename,$(LANG_INC_LIBRARY)),-and \( $(LANG_INC_LIBRARY) -false \),))
$(eval LANG_LIBRARY_FILE := $(shell find $(SRC_DIR) -type f -not -name "*.ipynb" $(LANG_LIBRARY_OPT) | sort))

$(eval BUILD_JUPYTER_FILE := $(patsubst $(SRC_DIR)/%,$(BUILD_SUBDIR)/%,$(LANG_JUPYTER_FILE)))
$(eval BUILD_NOTE_DST = $(foreach file, $(BUILD_JUPYTER_FILE), $(if $(filter $(foreach md,$(MARKDOWNIFY),$(md).ipynb), $(notdir $(file))), , $(file))))
$(eval BUILD_MARK_SRC = $(foreach file, $(BUILD_JUPYTER_FILE), $(if $(filter $(foreach md,$(MARKDOWNIFY),$(md).ipynb), $(notdir $(file))), $(file), )))
$(eval BUILD_MARK_DST := $(foreach ext,$(MARKDOWNIFY_EXTS),$(patsubst %.ipynb,%.$(ext),$(BUILD_MARK_SRC))))
$(eval BUILD_FILE := $(BUILD_NOTE_DST) $(BUILD_MARK_DST))

$(1)_$(2) : $(PRODUCT_SUBDIR)
$(PRODUCT_SUBDIR) : $(1)_$(2)-test $(1)_$(2)-mark $(BUILD_FILE) $(LANG_LIBRARY_FILE) $(ROOT_FILE)
	@echo "$(ECHO_PREFIX)[deploy] copy to $$@"
	mkdir -p $$@
ifneq ($(strip $(ROOT_FILE)),)
	cd $(PROJECT_DIR) && tar -cf - $(patsubst $(PROJECT_DIR)/%,%,$(ROOT_FILE)) | tar -xf - -C $$@
endif
ifneq ($(strip $(LANG_LIBRARY_FILE)),)
	cd $(SRC_DIR) && tar -cf - $(patsubst $(SRC_DIR)/%,%,$(LANG_LIBRARY_FILE)) | tar -xf - -C $$@
endif
ifneq ($(strip $(BUILD_FILE)),)
	cd $(BUILD_SUBDIR) && tar -cf - $(patsubst $(BUILD_SUBDIR)/%,%,$(BUILD_FILE)) | tar -xf - -C $$@
endif
	@echo "$(ECHO_SUFFIX)"

$(1)_$(2)-dist : $(PRODUCT_SUBDIR).zip
$(PRODUCT_SUBDIR).zip : $(1)_$(2)-test $(1)_$(2)-mark $(LANG_LIBRARY_FILE) $(ROOT_FILE)
	@echo "$(ECHO_PREFIX)[dist] zip to $$@"
	mkdir -p $$(@D)
ifneq ($(strip $(ROOT_FILE)),)
	cd $(PROJECT_DIR) && zip -rq $$@ $(patsubst $(PROJECT_DIR)/%,%,$(ROOT_FILE))
endif
ifneq ($(strip $(LANG_LIBRARY_FILE)),)
	cd $(SRC_DIR) && zip -rq $$@ $(patsubst $(SRC_DIR)/%,%,$(LANG_LIBRARY_FILE))
endif
ifneq ($(strip $(BUILD_FILE)),)
	cd $(BUILD_SUBDIR) && zip -rq $$@ $(patsubst $(BUILD_SUBDIR)/%,%,$(BUILD_FILE))
endif
	@echo "$(ECHO_SUFFIX)"

$(1)_$(2)-mark : $(BUILD_MARK_DST)

$(1)_$(2)-test : test-init $(BUILD_JUPYTER_FILE)
ifneq ($(strip $(BUILD_JUPYTER_FILE)),)
	@echo "$(ECHO_PREFIX)[test] $(1)_$(2)"
	python $(PROJECT_DIR)/tool/check_and_fix_notebook.py $(BUILD_JUPYTER_FILE) --is_build
ifeq ($(2), ex)
	nbqa ruff $(BUILD_JUPYTER_FILE) --ignore=B007,F401,F841
else
	nbqa ruff $(BUILD_JUPYTER_FILE)
endif
	@echo "$(ECHO_SUFFIX)"
endif

$(BUILD_SUBDIR)/%.pdf : $(BUILD_SUBDIR)/%.ipynb
	@echo "$(ECHO_PREFIX)[ipynb -> pdf] $$@"
	jupyter nbconvert --to webpdf $$<
	@echo "$(ECHO_SUFFIX)"

$(BUILD_SUBDIR)/%.md : $(BUILD_SUBDIR)/%.ipynb
	@echo "$(ECHO_PREFIX)[ipynb -> md] $$@"
	jupyter nbconvert --to markdown $$<
	@echo "$(ECHO_SUFFIX)"

$(BUILD_SUBDIR)/%.html : $(BUILD_SUBDIR)/%.ipynb
	@echo "$(ECHO_PREFIX)[ipynb -> html] $$@"
	jupyter nbconvert --to html $$<
	@echo "$(ECHO_SUFFIX)"

$(BUILD_SUBDIR)/%.ipynb : $(SRC_DIR)/%.ipynb
	@echo "$(ECHO_PREFIX)[build] $$@"
	mkdir -p $$(@D)
	python $(PROJECT_DIR)/tool/build.py $$< --output_dir $$(@D) --lang $(1) --mode $(2)
	@echo "$(ECHO_SUFFIX)"

endef
$(foreach mode,$(MODES),$(foreach lang,$(LANGUAGES),$(eval $(call MACRO_LANG_MODE_BUILD,$(lang),$(mode)))))
