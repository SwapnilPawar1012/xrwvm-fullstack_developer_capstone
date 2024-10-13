import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';


const PostReview = () => {
    const [dealer, setDealer] = useState({});
    const [review, setReview] = useState("");
    const [model, setModel] = useState();
    const [year, setYear] = useState("");
    const [date, setDate] = useState("");
    const [carmodels, setCarmodels] = useState([]);

    let curr_url = window.location.href;
    let root_url = curr_url.substring(0, curr_url.indexOf("postreview"));
    let params = useParams();
    let id = params.id;
    let dealer_url = root_url + `djangoapp/dealer/${id}`;
    let review_url = root_url + `djangoapp/add_review`;
    let carmodels_url = root_url + `djangoapp/get_cars`;

    const postreview = async () => {
        let name = sessionStorage.getItem("firstname") + " " + sessionStorage.getItem("lastname");

        // If the first and second name are stored as null, use the username
        if (name.includes("null")) {
            name = sessionStorage.getItem("username");
        }

        if (!model || review === "" || date === "" || year === "" || model === "") {
            alert("All details are mandatory");
            return;
        }

        let model_split = model.split(" ");
        let make_chosen = model_split[0];
        let model_chosen = model_split[1];

        let jsoninput = JSON.stringify({
            "name": name,
            "dealership": id,
            "review": review,
            "purchase": true,
            "purchase_date": date,
            "car_make": make_chosen,
            "car_model": model_chosen,
            "car_year": year,
        });

        console.log(jsoninput);

        // Get the CSRF token from cookies
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        const csrftoken = getCookie('csrftoken'); // Get CSRF token

        const res = await fetch(review_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken, // Include CSRF token in headers
            },
            body: jsoninput,
        });

        const json = await res.json();
        if (json.status === 200) {
            window.location.href = window.location.origin + "/dealer/" + id;
        } else {
            alert("Error posting review: " + json.message || "An unknown error occurred.");
        }
    };


    const get_dealer = async () => {
        alert("Fetching dealer..."); // Alert for fetching start
        try {
            const res = await fetch(dealer_url, {
                method: "GET"
            });

            if (!res.ok) {
                // Handle HTTP errors
                const errorText = await res.text();
                throw new Error(`Error fetching dealer: ${res.status} ${errorText}`);
            }

            const retobj = await res.json();

            // Check if the response has the expected structure
            if (retobj.status === 200 && retobj.dealer) {
                const dealerobjs = Array.isArray(retobj.dealer) ? retobj.dealer : [retobj.dealer];

                if (dealerobjs.length > 0) {
                    alert(`Dealer: ${JSON.stringify(dealerobjs[0])}`); // Use JSON.stringify to properly show object
                    setDealer(dealerobjs[0]);
                }
            } else {
                alert("No dealer found or unexpected response format.");
            }
        } catch (error) {
            console.error("Fetch error:", error);
            alert(`An error occurred: ${error.message}`); // Display error to user
        }
    };


    const get_cars = async () => {
        alert("Fetching cars..."); // Alert for fetching start
        try {
            const res = await fetch(carmodels_url, {
                method: "GET"
            });

            if (!res.ok) {
                // Handle HTTP errors
                const errorText = await res.text();
                throw new Error(`Error fetching car models: ${res.status} ${errorText}`);
            }

            const retobj = await res.json();

            // Check if CarModels exists and is an array
            if (retobj.CarModels && Array.isArray(retobj.CarModels)) {
                const carmodelsarr = retobj.CarModels; // Directly assign if it's already an array
                alert(`Cars: ${JSON.stringify(carmodelsarr)}`); // Use JSON.stringify for proper display
                setCarmodels(carmodelsarr);
            } else {
                alert("No car models found or unexpected response format.");
            }
        } catch (error) {
            console.error("Fetch error:", error);
            alert(`An error occurred: ${error.message}`); // Display error to user
        }
    };


    useEffect(() => {
        get_dealer();
        get_cars();
    }, []);


    return (
        <div>
            <Header />
            <div style={{ margin: "5%" }}>
                <h1 style={{ color: "darkblue" }}>{dealer.full_name}</h1>
                <textarea id='review' cols='50' rows='7' onChange={(e) => setReview(e.target.value)}></textarea>
                <div className='input_field'>
                    Purchase Date <input type="date" onChange={(e) => setDate(e.target.value)} />
                </div>
                <div className='input_field'>
                    Car Make
                    <select name="cars" id="cars" onChange={(e) => setModel(e.target.value)}>
                        <option value="" selected disabled hidden>Choose Car Make and Model</option>
                        {carmodels.map(carmodel => (
                            <option value={carmodel.CarMake + " " + carmodel.CarModel}>{carmodel.CarMake} {carmodel.CarModel}</option>
                        ))}
                    </select>
                </div >

                <div className='input_field'>
                    Car Year <input type="int" onChange={(e) => setYear(e.target.value)} max={2023} min={2015} />
                </div>

                <div>
                    <button className='postreview' onClick={postreview}>Post Review</button>
                </div>
            </div>
        </div>
    )
}
export default PostReview
