define(['jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore',
    'arches',
    'edtfy',
    'moment',
    'bootbox'], function ($, Backbone, ko, koMapping, _, arches, edtfy, moment, bootbox) {
    return Backbone.View.extend({

        events: {
            'click .add-button': 'addItem',
            'click [name="discard-edit-link"]': 'undoCurrentEdit'
        },

        initialize: function(options) {
            var self = this;
            this.singleEdit = false;

            _.extend(this, options);
         
            this.defaults = [];
            this.viewModel = JSON.parse(JSON.stringify(this.data[this.dataKey]));
            //this.viewModel.domains = this.data[this.dataKey].domains;
            this.viewModel.branch_lists = koMapping.fromJS(this.data[this.dataKey].branch_lists);

            // if this is a function then it's assumed to be an observableArray already
            if(typeof this.viewModel !== 'function'){
                _.each(this.viewModel.branch_lists(), function(item){
                    item.editing = ko.observable(false);
                }, this);      

                _.each(this.viewModel.defaults, function(value, entitytypeid){
                    this.addDefaultNode(entitytypeid, 'value', value);
                }, this);   
            }

            if (this.singleEdit) {
                _.each(this.viewModel.branch_lists(), function (branch) {
                    if (branch) {
                        this.originalItem = koMapping.toJS(branch);
                        branch.editing(true);
                        _.each(branch.nodes(), function (node) {
                            node.value.subscribe(function() {
                                this.trigger('change', 'edit', branch);
                                this.validate();
                            }, this);
                        }, this);
                    }
                }, this);
            }

            ko.applyBindings(this, this.el);
        },

        validate: function(){
            var valid = true;
            _.each(this.viewModel.branch_lists(), function(list){
                if (this.singleEdit || !list.editing()){
                    valid = valid && this.validateBranch(ko.toJS(list.nodes));
                }
            }, this); 
            return valid;
        },

        validateBranch: function (data) {
            return true;
        },

        validateHasValues: function(nodes){
            var valid = nodes != undefined && nodes.length > 0;
            _.each(nodes, function (node) {
                if (node.entityid === '' && node.value === ''){
                    valid = false;
                }
            }, this);
            return valid;
        },
        		
	 	 validateEdtfy: function(nodes){
       		var valid = nodes !== undefined && nodes.length > 0;
			_.each(nodes, function(node) {
				if (node.entityid === '' && node.value === '') {
					valid = false;
				} else {
					/* if this is an interval, allow for current use */
					if (node.entityid == 'TO_DATE.E49' && node.value == 'open') {
						valid = true;
					} else {
						/* if the value is a cidoc E49, validate further */
						var entityid = node.entitytypeid.slice(-3);
						if (entityid == 'E49') {			
							/* check for leading or trailing white spaces */
							var original = node.value.length;
							var trim = node.value.trim();
							var trimmed = trim.length;
							if (original != trimmed) {
								bootbox.alert('Please check for spaces before or after your date.');
								valid = false;
							} else {						
								/* use moment.js to check for a correct date format first */
								var formats = ["YYYY-MM-DD", "YYYY-MM"]; 
								var initial = moment(node.value, formats, true).isValid();
								if (initial === true) {
									valid = true;
								} else {
									/* node.value is not strictly valid as a date, so check if it fits edtf */
									edtfy = require('edtfy');
									edtfy.locale('en');
									try {
			    						var parsed = edtfy(node.value); 
										if(parsed == node.value) {
											/* user entered a correct edtf value */
											valid = true;
										} else {
											/* user used a recognizable invalid format, suggest edit */
											bootbox.alert('Try entering this instead: ' + parsed);
											valid = false;
										}
									}
									catch(err) {
										valid = false;
									}							
								}
							}
						}
					}
				}
			}, this);
			return valid;
 		},

        getEditedNode: function(entitytypeid, key){
            this.addDefaultNode(entitytypeid, key, '');
            return ko.pureComputed({
                read: function() {
                    var ret = null;
                    var list = this.getEditedBranch();
                    _.each(list.nodes(), function(node){
                        if (entitytypeid.search(node.entitytypeid()) > -1){
                            ret = node[key]();
                        }
                    }, this);
                    if(ret === null){
                        _.each(this.defaults, function(defaultNode){
                            if (defaultNode.entitytypeid === entitytypeid){
                                var node = koMapping.fromJS(defaultNode);
                                if(this.singleEdit){
                                    node.value.subscribe(function() {
                                        this.trigger('change', 'edit', list);
                                        this.validate();
                                    }, this);
                                } 
                                list.nodes.push(node); 
                            }
                        }, this);
                    }
                    return ret
                },
                write: function(value){
                    _.each(this.viewModel.branch_lists(), function(list){
                        if(list.editing()){
                            _.each(list.nodes(), function(node){
                                if (entitytypeid.search(node.entitytypeid()) > -1){
                                    if(typeof value === 'string'){
                                        node[key](value);
                                    }else{
                                        _.each(value, function(val, k, list){
                                            node[k](val);
                                        }, this);
                                    }
                                }
                            }, this);
                        }
                    }, this);
                },
                owner: this
            }).extend({rateLimit: 50});
        },

        getBranchLists: function() {
            var branch_lists = [];
            _.each(this.viewModel.branch_lists(), function(list){
                if(!list.editing() || (this.singleEdit && list.editing())){
                    branch_lists.push(list);
                }
            }, this);
            return branch_lists;
        },

        addDefaultNode: function(entitytypeid, key, value){
            var alreadyHasDefault = false;
            var def = {
                property: '',
                entitytypeid: entitytypeid,
                entityid: '',
                value: '',
                label: '',
                businesstablename: '',
                child_entities: []
            };
            def[key] = value;
            _.each(this.defaults, function(node){
                if (node.entitytypeid === entitytypeid){
                    alreadyHasDefault = true;
                }
            }, this);

            if (!alreadyHasDefault){
                this.defaults.push(def); 
            }

            return def
        },

        addItem: function() {
            var branch = this.getEditedBranch();
            var validationAlert = this.$el.find('.branch-invalid-alert');                        
            if (this.validateBranch(ko.toJS(branch.nodes))) {
                var branch = this.getEditedBranch();
                branch.editing(false);
                this.addBlankEditBranch();
                this.originalItem = null;
                this.trigger('change', 'add', branch);
            } else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        deleteItem: function(branch, e) {
            this.viewModel.branch_lists.remove(branch);
            this.trigger('change', 'delete', branch);   
        },

        editItem: function(branch, e) {        
            this.originalItem = koMapping.toJS(branch);
            this.removeEditedBranch();
            branch.editing(true);
            
            this.trigger('change', 'edit', branch);
        },

        getEditedBranch: function(){
            var editedBranch = null;
            _.each(this.viewModel.branch_lists(), function(list){
                if(list.editing()){
                    editedBranch = list;
                }
            }, this);
            if(editedBranch === null){
                editedBranch = this.addBlankEditBranch();
            } 
            return editedBranch;
        },

        addBlankEditBranch: function(){
            var branch = koMapping.fromJS({
                'editing':ko.observable(true), 
                'nodes': ko.observableArray(this.defaults)
            });
            this.viewModel.branch_lists.push(branch); 
            _.each(branch.nodes(), function(node){
                if(this.singleEdit){
                    node.value.subscribe(function() {
                        this.trigger('change', 'edit', branch);
                        this.validate();
                    }, this);
                } 
            }, this);            
            return branch;
        },

        removeEditedBranch: function(){
            var branch = this.getEditedBranch();
            this.viewModel.branch_lists.remove(branch); 
            return branch;
        },

        undoCurrentEdit: function() {
            this.removeEditedBranch();
            this.addBlankEditBranch();
            if(this.originalItem !== null){
                this.viewModel.branch_lists.push(koMapping.fromJS(_.extend({editing: false}, this.originalItem)));

                this.originalItem = null;  
            }         
        },

        getData: function(){
            var data = koMapping.toJS(this.getBranchLists());
            _.each(data, function(item){
                var i = item;
                delete item.editing;
            }, this); 
            return data
        },

        undoAllEdits: function(){
            this.viewModel.branch_lists.removeAll();
            _.each(this.data[this.dataKey].branch_lists, function(item){
                this.viewModel.branch_lists.push(koMapping.fromJS(_.extend({editing: this.singleEdit}, item)));
            }, this); 

            if(!this.singleEdit || this.viewModel.branch_lists().length === 0){
                this.addBlankEditBranch();
            }
        }
    });
});