// DOM Elements
const scrollToTopBtn = document.querySelector(".scrollToTopBtn");
const themeBtn = document.querySelector(".themeBtn");
const profileBtn = document.querySelector(".profileBtn");
const profileMenu = document.querySelector(".profileMenu");
const nav = document.querySelector("nav");
const navScroll = document.querySelector(".nav__onScroll");
const navDropdown = document.querySelector(".nav__dropdown");
const navDropdownBtn = document.querySelector(".nav__dropdownBtn");
const projectCards = Array.from(document.getElementsByClassName("section__projectCard"));
const pastProjectCards = Array.from(document.getElementsByClassName("section__pastProjectCard"));

// theme handling
const headTag = document.getElementsByTagName("head")[0];
const darkCSS = document.createElement("link");
darkCSS.rel = "stylesheet";
darkCSS.type = "text/css";
darkCSS.href = "/static/ftp/ProjectsPage/css/dark.css";

const themeHandler = () => {
    const mode = themeBtn.classList.contains("fa-moon") ? "light" : "dark";
    if (mode === "light") darkMode();
    else lightMode();
};
const darkMode = () => {
    themeBtn.classList.remove("fa-moon");
    themeBtn.classList.add("fa-sun");
    localStorage.setItem("irc_ftp", JSON.stringify({ theme: "dark" }));
    headTag.appendChild(darkCSS);
    // nav handling
    navScroll.classList.remove("nav__onScroll");
    navScroll.querySelector(".nav__logo").src = "/static/ftp/ProjectsPage/img/logo/ftp_logo.png"
};
const lightMode = () => {
    themeBtn.classList.remove("fa-sun");
    themeBtn.classList.add("fa-moon");
    localStorage.setItem("irc_ftp", JSON.stringify({ theme: "light" }));
    headTag.removeChild(darkCSS);
    // nav handling
    navScroll.classList.add("nav__onScroll");
    navScroll.querySelector(".nav__logo").src = "/static/ftp/ProjectsPage/img/logo/ftp_logo2.png"
};
// setting theme from localstorage
const prevTheme = JSON.parse(localStorage.getItem("irc_ftp"))?.theme;
if (prevTheme === "dark")
    darkMode()
// fix to dark mode enabling flash onload
// setTimeout(() => document.querySelector("section").style.transition = "background-color 0.5s", 500);

// scroll events
const scrollToTop = () => {
    window.scrollTo(0, 0);
};

window.addEventListener("scroll", () => {
    if (window.scrollY >= 2) {
        // nav
        nav.style.display = "none";
        navScroll.style.display = "flex";
        // floating buttons
        scrollToTopBtn.style.transform = "scale(1)";
        // footer-nav
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1) {
            setTimeout(() => navScroll.style.display = "none", 500);
            navScroll.style.animation = "nav__disappear 0.5s ease-out 1";
        }
        else {
            navScroll.style.display = "flex";
            navScroll.style.animation = "nav__appear 0.5s ease-out 1";
        }
    }
    else {
        // nav
        nav.style.display = "flex";
        navScroll.style.display = "none";
        // floating buttons
        scrollToTopBtn.style.transform = "scale(0)";
    }
    // card transitions
    pastProjectCards.map(projectCard => {
        if (projectCard.getBoundingClientRect().y < projectCard.clientHeight + 150) {
            projectCard.style.animation = "projectCard__appear 0.5s ease-out 1 forwards";
        }
        else {
            projectCard.style.animation = "projectCard__disappear 0.5s ease-out 1 forwards";
        }
    });
});

// grid
let projectCardTimeout;
let isOtherProjectOpen = false;

projectCards.map(projectCard => {
    projectCard.querySelector(".js-expander").addEventListener("click", () => {
        if (projectCard.classList.contains("is-collapsed")) {
            projectCards.map(projectCard => {
                projectCard.classList.remove("is-expanded");
                projectCard.classList.add("is-collapsed");
                projectCard.style.zIndex = 0;
            });
            clearTimeout(projectCardTimeout);
            projectCardTimeout = setTimeout(() => {
                projectCard.classList.remove("is-collapsed");
                projectCard.classList.add("is-expanded");
                projectCard.style.zIndex = 1;
                window.scrollTo(0, projectCard.offsetTop + projectCard.querySelector(".section__projectCardInner").clientHeight - (Math.max(nav.clientHeight, navScroll.clientHeight)) - 20);
            }, isOtherProjectOpen ? 300 : 0);

            // switch isOtherProjectOpen
            isOtherProjectOpen = true;
        }
        else {
            projectCard.classList.remove("is-expanded");
            projectCard.classList.add("is-collapsed");
            projectCard.style.zIndex = 0;
            window.scrollTo(0, projectCard.offsetTop - (Math.max(nav.clientHeight, navScroll.clientHeight)) - 20);
            isOtherProjectOpen = false;
        }
    });

    projectCard.querySelector(".js-collapser").addEventListener("click", () => {
        projectCard.classList.remove("is-expanded");
        projectCard.classList.add("is-collapsed");
        projectCard.style.zIndex = 0;
        window.scrollTo(0, projectCard.offsetTop - (Math.max(nav.clientHeight, navScroll.clientHeight)) - 20);
        isOtherProjectOpen = false;
    });
});


// form handling
let isUploadedCV = false;
let isValidCV = true;

const openForm = (projectId) => {
    console.log(projectId);
    const projectForm = document.getElementById("project-" + projectId);
    console.log(projectForm);
    document.body.style.overflow = "hidden";

    navScroll.style.animation = "nav__disappear 0.5s ease-out 1 forwards";
    scrollToTopBtn.style.transform = "scale(0)";
    profileBtn.style.opacity = "0";
    // themeBtn.style.opacity = "0";
    setTimeout(() => {
        profileBtn.style.zIndex = "-1"
        // themeBtn.style.zIndex = "-1"
    }, 500);

    projectForm.parentElement.style.display = "grid";
    projectForm.style.display = "flex";
    projectForm.style.animation = "form__appear 0.3s ease-out 1 forwards";
};

const closeForm = (projectId) => {
    const projectForm = document.getElementById("project-" + projectId);
    document.body.style.overflow = "auto";

    navScroll.style.animation = "nav__appear 0.5s ease-out 1 forwards";
    scrollToTopBtn.style.transform = "scale(1)";
    profileBtn.style.zIndex = "4";
    profileBtn.style.opacity = "1";
    // themeBtn.style.zIndex = "4";
    // themeBtn.style.opacity = "1";

    projectForm.style.animation = "form__disappear 0.3s ease-out 1 forwards";
    setTimeout(() => {
        projectForm.style.display = "none";
        projectForm.parentElement.style.display = "none";
    }, 300);
};

const submitProjectForm = (e) => {
    e.preventDefault();

    const formElement = e.target.parentElement;

    if (e.target.classList.contains("projectForm__disabledBtn"))
        openWordCountAlert(e);
    else {
        if (!isUploadedCV) {
            const fileConfirmation = confirm("Are you sure you want to apply with your default CV?");
            if (fileConfirmation)
                formElement.submit();
        }
        else
            formElement.submit();
    }
}

const openWordCountAlert = (e) => {
    const sop = e.target.parentElement.querySelector(".projectForm__ftpSOP").value;
    const loi = e.target.parentElement.querySelector(".projectForm__ftpLOI")?.value;

    const wordCountAlert = e.target.parentElement.querySelector(".projectForm__wordCountAlert");

    if (e.target.classList.contains("projectForm__disabledBtn")) {
        const sopWordCount = sop.split(" ").length - 1;
        const loiWordCount = loi ? loi.split(" ").length - 1 : undefined;

        wordCountAlert.firstElementChild.innerText = loiWordCount ? "SOP word count: " + sopWordCount + "\nLOI word count: " + loiWordCount : "SOP word count: " + sopWordCount;

        wordCountAlert.style.zIndex = "1";
        wordCountAlert.style.opacity = "1";
    }
};

const closeWordCountAlert = (e) => {
    const wordCountAlert = e.target.parentElement.querySelector(".projectForm__wordCountAlert");

    wordCountAlert.style.opacity = "0";
    wordCountAlert.style.zIndex = "-1";
};

const wordCountCheck = (e) => {
    const project = e.target.parentElement.parentElement;
    const sop = project.querySelector(".projectForm__ftpSOP");
    const loi = project.querySelector(".projectForm__ftpLOI");
    const submitBtn = project.querySelector(".projectForm__submitBtn");

    const sopWordCount = sop.value.split(" ").length - 1;
    const loiWordCount = loi ? loi.value.split(" ").length - 1 : undefined;

    if (!loi && sopWordCount >= 150 && sopWordCount <= 200)
        submitBtn.classList.remove("projectForm__disabledBtn");
    else if (loi && sopWordCount >= 150 && sopWordCount <= 200 && loiWordCount <= 500)
        submitBtn.classList.remove("projectForm__disabledBtn");
    else
        submitBtn.classList.add("projectForm__disabledBtn");
};

// profile menu handling
let profileMenuTimeout;
const profileMenuHandler = () => {
    const display = profileMenu.style.display;
    if (!display || display === "none")
        setTimeout(() => openProfileMenu(), 0);
    else
        closeProfileMenu();
};
const openProfileMenu = () => {
    profileMenu.style.display = "flex";
    profileMenu.style.animation = window.innerWidth >= 800 ? "menuAppear 0.2s ease-out 1 forwards" : "menuAppear_phone 0.2s ease-out 1 forwards";
    closeDropdown();
};
const closeProfileMenu = () => {
    clearTimeout(profileMenuTimeout);
    profileMenuTimeout = setTimeout(() => profileMenu.style.display = "none", 200);
    profileMenu.style.animation = window.innerWidth >= 800 ? "menuDisappear 0.2s ease-out 1 forwards" : "menuDisappear_phone 0.2s ease-out 1 forwards";
};
profileMenu.addEventListener("click", closeProfileMenu);

// Drop down menu
let dropdownTimeout;
const dropdownHandler = () => {
    const display = navDropdown.style.display;
    if (!display || display === "none")
        setTimeout(() => openDropdown(), 0);
    else
        closeDropdown();
};
const openDropdown = () => {
    navDropdown.style.display = "flex";
    navDropdown.style.animation = "nav__dropdownAppear 0.2s ease-out 1 forwards";
    closeProfileMenu();
};
const closeDropdown = () => {
    clearTimeout(dropdownTimeout);
    dropdownTimeout = setTimeout(() => navDropdown.style.display = "none", 200);
    navDropdown.style.animation = "nav__dropdownDisappear 0.2s ease-out 1 forwards";
};
navDropdown.addEventListener("click", closeDropdown);

// fix
window.addEventListener("click", () => {
    if (navDropdown.style.display === "flex")
        closeDropdown();
    else if (profileMenu.style.display === "flex")
        closeProfileMenu();
});

// upload file
const truncate = (str, n) => {
    return (str.length > n) ? str.substr(0, n - 1) + "..." : str;
};

const uploadFile = (e) => {
    e.preventDefault();
    e.target.previousElementSibling.click();
};

const changedFile = (e) => {
    const fileInput = e.target;
    const uploadedFile = e.target.files[0];

    const fileConfirmation = confirm("Are you sure you want to apply with a different CV than your default one?");

    if (!uploadedFile.name.endsWith(".pdf")) {
        alert("Please, upload your CV in pdf format");
        fileInput.value = "";
        fileInput.nextElementSibling.innerText = "Apply with a different CV";
        isValidCV = false;
        isUploadedCV = false;
        return;
    }
    else if (fileConfirmation) {
        fileInput.nextElementSibling.innerText = "Uploaded: \"" + truncate(uploadedFile.name, 20) + "\"";
        isValidCV = true;
        isUploadedCV = true;
    }
};