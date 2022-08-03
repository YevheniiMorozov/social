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
    setTimeout(()=> {fetch("/user_tags/")
      .then(response => response.json())
      .then(data => (this.tags = data));
    }, 500)
    }
  },
});
app.mount("#app");

