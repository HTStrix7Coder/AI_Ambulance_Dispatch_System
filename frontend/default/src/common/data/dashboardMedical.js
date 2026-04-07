
// Import Images
import avatar1 from "../../assets/images/users/avatar-1.jpg";
import avatar2 from "../../assets/images/users/avatar-2.jpg";
import avatar3 from "../../assets/images/users/avatar-3.jpg";
import avatar4 from "../../assets/images/users/avatar-4.jpg";
import avatar6 from "../../assets/images/users/avatar-6.jpg";

const medicalWidgets = [
    {
        id: 1,
        cardColor: "primary",
        label: "Total Patients",
        badge: "ri-arrow-right-up-line",
        badgeClass: "success",
        percentage: "+12.24",
        counter: "1200",
        link: "View all patients",
        bgcolor: "success",
        icon: "bx bx-user-plus",
        decimals: 0,
        prefix: "",
        suffix: ""
    },
    {
        id: 2,
        cardColor: "secondary",
        label: "Pending Cases",
        badge: "ri-arrow-right-down-line",
        badgeClass: "danger",
        percentage: "-2.57",
        counter: "75",
        link: "View all cases",
        bgcolor: "info",
        icon: "bx bx-folder-open",
        decimals: 0,
        prefix: "",
        separator: ",",
        suffix: ""
    },
    {
        id: 3,
        cardColor: "success",
        label: "New Appointments",
        badge: "ri-arrow-right-up-line",
        badgeClass: "success",
        percentage: "+19.08",
        counter: "32",
        link: "See details",
        bgcolor: "warning",
        icon: "bx bx-calendar-plus",
        decimals: 0,
        prefix: "",
        suffix: ""
    },
    {
        id: 4,
        cardColor: "info",
        label: "Occupancy Rate",
        badgeClass: "muted",
        percentage: "+0.00",
        counter: "85.5",
        link: "View details",
        bgcolor: "primary",
        icon: "bx bx-bed",
        decimals: 1,
        prefix: "",
        suffix: "%"
    },
];

const recentCases = [
    {
        id: 1,
        caseId: "#CASE2112",
        img: avatar1,
        name: "Alex Smith",
        doctor: "Dr. Johnson",
        date: "05 Nov, 2025",
        priority: "High",
        priorityClass: "danger",
        status: "Pending",
        statusClass: "warning",
    },
    {
        id: 2,
        caseId: "#CASE2111",
        img: avatar2,
        name: "Jansh Brown",
        doctor: "Dr. Williams",
        date: "04 Nov, 2025",
        priority: "Medium",
        priorityClass: "warning",
        status: "In Progress",
        statusClass: "info",
    },
    {
        id: 3,
        caseId: "#CASE2109",
        img: avatar3,
        name: "Ayaan Bowen",
        doctor: "Dr. Brown",
        date: "04 Nov, 2025",
        priority: "Low",
        priorityClass: "success",
        status: "Completed",
        statusClass: "success",
    },
    {
        id: 4,
        caseId: "#CASE2108",
        img: avatar4,
        name: "Prezy Mark",
        doctor: "Dr. Jones",
        date: "03 Nov, 2025",
        priority: "High",
        priorityClass: "danger",
        status: "Pending",
        statusClass: "warning",
    },
    {
        id: 5,
        caseId: "#CASE2107",
        img: avatar6,
        name: "Vihan Hudda",
        doctor: "Dr. Miller",
        date: "02 Nov, 2025",
        priority: "Medium",
        priorityClass: "warning",
        status: "In Progress",
        statusClass: "info",
    },
];

export { medicalWidgets, recentCases };
