var FeatureModel = function(data){
	var self = this;
  ko.mapping.fromJS(data, {}, self);	
}

function FormViewModel(){
  var self = this;

  self.title = ko.observable("");
  self.description = ko.observable("");
  self.clients = ko.observableArray([
    'Client A',
    'Client B',
    'Client C',
    'Client D',
  ]);
  self.selected_client = ko.observable();
  self.client_priority = ko.observable("");
  self.target_date = ko.observable("");
  self.product_areas = ko.observableArray([
    'Policies',
    'Billing',
    'Claims',
    'Reports'
  ]);
  self.selected_product_area = ko.observable();

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

  self.save = function (){
    $.ajax("/api/v1/feature", {
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(self.post_data()),
      success: function(data,status){
        self.refresh()
        self.title(null);
        self.description(null);
        self.selected_client(null);
        self.client_priority(null);
        self.target_date(null);
        self.selected_product_area(null);
      }
    });
  }


  // --------------
  //   Feature Requests List section
  // ---------------
  self.feature_requests = ko.observableArray([]);
  self.edit = ko.observable(true);

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
    //if (elem.nodeType === 1) $(elem).slideUp(function() { $(elem).remove()});
    if (elem.nodeType === 1)  $(elem).remove();
  }
}

ko.applyBindings(new FormViewModel());
