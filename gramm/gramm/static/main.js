const app = Vue.createApp({
  delimiters: ["[[", "]]"],
  data() {
    return {
      message: "Tag:",
      tags: [],
    };
  },
  methods: {
    getListTags(){
    fetch("/user_tags/")
      .then(response => response.json())
      .then(data => (this.tags = data));
    }
  },
});
app.mount("#app");

