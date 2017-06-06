var FeatureModel = function(data){
	var self = this;
  ko.mapping.fromJS(data, {}, self);	
}

function FormViewModel(){
  var self = this;

  self.clients = ko.observableArray([
    'Client A',
    'Client B',
    'Client C',
    'Client D',
  ]);
  self.product_areas = ko.observableArray([
    'Policies',
    'Billing',
    'Claims',
    'Reports'
  ]);
  self.title = ko.observable("").extend({required: true});
  self.description = ko.observable("").extend({required: true});
  self.selected_client = ko.observable().extend({required: true});
  self.client_priority = ko.observable("1").extend({required: true, number: true});
  self.target_date = ko.observable("").extend({required: true});
  self.selected_product_area = ko.observable().extend({required: true});
  self.form_success = ko.observable(null);

  self.form_success_toggle = function(){
    if (self.form_success()){
      self.form_success(null);
    } else {
      self.form_success(true);
      setTimeout(function(){
        self.form_success(null);
      },4000);
    }
  }
  self.post_data = ko.computed(function(){
    return {
      title: self.title(),
      description: self.description(),
      client: self.selected_client(),
      client_priority: self.client_priority(),
      target_date: self.target_date(),
      product_area: self.selected_product_area()
    }
  });

  self.form_errors = ko.validation.group({
    title: self.title,
    description: self.description,
    selected_client: self.selected_client,
    client_priority: self.client_priority,
    target_date: self.target_date,
    selected_product_area: self.selected_product_area
  });
  self.validate_form = function(){
      //self.title.isValid(),
      //self.description.isValid(),
      //self.selected_client.isValid(),
      //self.client_priority.isValid(),
      //self.target_date.isValid(),
      //self.selected_product_area.isValid()
    form_items = {
      title: self.title.isValid(),
      description: self.description.isValid(),
      client: self.selected_client.isValid(),
      client_priority: self.client_priority.isValid(),
      target_date: self.target_date.isValid(),
      product_area: self.selected_product_area.isValid()
    }
    for (var k in form_items){
      if (form_items.hasOwnProperty(k)){
        if (!form_items[k]) {return false;}
      }
    }
    return true;
  }

  self.save = function (){
    if (self.validate_form()){
      $.ajax("/api/v1/feature", {
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(self.post_data()),
        success: function(data,status){
          self.refresh()
          self.title(null);
          self.description(null);
          self.selected_client(null);
          self.client_priority("1");
          self.target_date(null);
          self.selected_product_area(null);
          // reset form after submit
          self.title.isModified(false);
          self.description.isModified(false);
          self.selected_client.isModified(false);
          self.client_priority.isModified(false);
          self.target_date.isModified(false);
          self.selected_product_area.isModified(false);
          //show success message
          self.form_success_toggle();
        }
      });
    } else {
      self.form_errors.showAllMessages(true);
    }
  }


  // --------------
  //   Feature Requests List section
  // ---------------

  // -- Bindings
  
  self.filter_visible = ko.observable(null);
  self.filter_visible_toggle = function(){
    console.log('something');
    if (self.filter_visible()){
      self.filter_visible(null);
    } else {
      self.filter_visible(true);
    }
  }
  self.feature_requests = ko.observableArray([]);
  self.edit = ko.observable(true);
  self.selected_client_filter = ko.observable();
  self.selected_product_area_filter = ko.observable();
  self.filter_clients = ko.observableArray([
    'Client A',
    'Client B',
    'Client C',
    'Client D',
  ]);
  self.filter_product_areas = ko.observableArray([
    'Policies',
    'Billing',
    'Claims',
    'Reports'
  ]);

  // -- Refresh
  self.refresh = function(){
    $.ajax("/api/v1/feature",{
      dataType: 'json',
      success: function(data){
        self.feature_requests([]);
        data.forEach(function(feature){
          fo = new FeatureModel(feature)
          self.feature_requests.push(fo)
        });
      }
    });
  }
  self.refresh() // refresh on load
  //setTimeout(function(){console.log(self.feature_requests());},3000);


  // -- Edit / Update / Delete

  self.edit_feature = function(data, event){
    var target = event.target;
    $(target).parents('.view-wrapper').fadeOut(400, function(){
      $(target).parents('.view-wrapper').next().fadeIn();
    });
    self.edit(null);
  }
  self.cancel_edit = function(data, event){
    self.refresh();
    self.edit(true);
  }
  self.update_feature = function(data, event){
    var target = event.target;
    fid = $(target).attr('id');
    feature_index = $(target).data('index');
    update_data = ko.mapping.toJS(self.feature_requests()[feature_index]);
    $.ajax("/api/v1/feature/"+fid,{
      method: 'PUT',
      data: JSON.stringify(update_data),
      dataType: 'json',
      contentType: 'application/json',
      success: function(){
        self.refresh();
        self.edit(true);
      }
  });
  }
  self.delete_feature = function(data, event){
    var target = event.target;
    fid = $(target).attr('id');
    $.ajax("/api/v1/feature/"+fid,{
      method: 'DELETE',
      dataType: 'json',
      success: function(){
        $(target).parents('.edit-wrapper').fadeOut();
        self.edit(true);
      }
    });
  }
  self.show_feature_request = function(elem){
    if (elem.nodeType === 1) $(elem).find('.view-wrapper').hide().slideDown();
  }
  self.delete_feature_request = function(elem){
    if (elem.nodeType === 1)  $(elem).remove();
  }

  // -- Filtering
  self.filter_by_client = ko.observable(null);
  self.filter_by_client_bool = ko.observable(null);
  self.filter_by_product_area = ko.observable(null);
  self.filter_by_product_area_bool = ko.observable(null);
  self.filter = ko.observable(true);
  self.filtered_feature_requests = ko.computed(function(){
    var filter = self.filter();
    if (!filter){
      return self.feature_requests();
    } else {
      filtered_clients = self.feature_requests().filter(function(feature){
        if (self.filter_by_client_bool()){
          return feature['client']() == self.filter_by_client();
        } else {
          return true;
        }
      });
      filtered_product_areas = filtered_clients.filter(function(feature){
        if (self.filter_by_product_area_bool()){
          return feature['product_area']() ==  self.filter_by_product_area();
        } else {
          return true;
        }
      });
      return filtered_product_areas;
    }
  });
}

ko.applyBindings(new FormViewModel());
