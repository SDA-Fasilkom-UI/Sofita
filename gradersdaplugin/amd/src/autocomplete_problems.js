define(["jquery"], function($) {
  return {
    processResults: function(_, results) {
      return results.map(elem => {
        return {
          value: elem,
          label: elem
        };
      });
    },

    transport: function(selector, query, callback) {
      let el = $(selector);
      let grader_url = el.data("grader_url");
      let url = grader_url + "/api/problems/?query=" + query;

      $.get(url, callback);
    }
  };
});
