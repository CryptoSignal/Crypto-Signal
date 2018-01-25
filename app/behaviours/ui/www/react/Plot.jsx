import React from 'react';

class Plot extends React.Component {
	constructor(props) {
		super(props);

		this.updatePlot = this.updatePlot.bind(this);

	}

	render() {
		return (
		    <div className="row">
              <div id="d3plot">
                <svg width="960" height="500">{/* D3 Plot goes Here */}</svg>
			  </div>
            </div>

		)
	}

	componentDidMount() {
	    this.updatePlot();
    }

    /* When component is being updated, erase the previous graph and replace it with new data */
    componentDidUpdate() {
        const windowWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);

	    $('#d3plot').html(`<svg width=${windowWidth} height="500"></svg>`);
	    this.updatePlot();
    }

	updatePlot() {
	    const svg = d3.select("svg"),
            margin = {top: 20, right: 50, bottom: 30, left: 50},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            // bisectDate = d3.bisector(function(d) { return d.date; }).left,
            // formatValue = d3.format(",.2f"),
            // formatCurrency = function(d) { return "$" + formatValue(d); };

	    const zoom = d3.zoom()
            .scaleExtent([1, 8])
            .translateExtent([[-100, -100], [width + 90, height + 100]])
            .on("zoom", zoomed);

        // const parseTime = d3.timeParse("%d-%b-%y");

        const x = d3.scaleLinear()
            .rangeRound([0, width]);

        const y = d3.scaleLinear()
            .rangeRound([height, 0]);

        const line = d3.line()
            .x(d => x(d[0]))
            .y(d => y(d[1]));

        x.domain(d3.extent(this.props.closingPrices, d => d[0] ));
        y.domain(d3.extent(this.props.closingPrices, d => d[1] ));

        const xAxis = d3.axisBottom(x);
        const yAxis = d3.axisLeft(y);

        const gX = g.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        gX.append("text")
            .attr("fill", "#000")
            .attr("y", -6)
            .attr("dx", width)
            .attr("text-anchor", "end")
            .text("Data Point #");

        const gY = g.append("g")
            .call(yAxis);

        const coinPair = $('#coin-pair').val();
        const baseCoin = coinPair.substring(coinPair.length - 3);

        gY.append("text")
            .attr("fill", "#000")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", "0.71em")
            .attr("text-anchor", "end")
            .text(`Price (${baseCoin})`);

        const inner = g.append("g");

        /* Plot the closing prices */
        const closings = inner.append("path")
            .attr("clip-path", "url(#clipped-path)")
            .datum(this.props.closingPrices)
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        const bollinger_upper = inner.append("path")
            .attr("clip-path", "url(#clipped-path)")
            .datum(this.props.indicators.bollinger_upper)
            .attr("fill", "none")
            .attr("stroke", "orange")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-dasharray", "5, 5")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        const bollinger_lower = inner.append("path")
            .attr("clip-path", "url(#clipped-path)")
            .datum(this.props.indicators.bollinger_lower)
            .attr("fill", "none")
            .attr("stroke", "orange")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-dasharray", "5, 5")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        const sma9 = inner.append("path")
            .attr("clip-path", "url(#clipped-path)")
            .datum(this.props.indicators.sma9)
            .attr("fill", "none")
            .attr("stroke", "red")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        const sma15 = inner.append("path")
            .attr("clip-path", "url(#clipped-path)")
            .datum(this.props.indicators.sma15)
            .attr("fill", "none")
            .attr("stroke", "green")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-width", 1.5)
            .attr("d", line);

        /* Plot all the buys as green dots */
        const buys = inner.selectAll("scatter-buys")
            .attr("clip-path", "url(#clipped-path)")
            .data(this.props.buys)
            .enter().append("svg:circle")
            .attr("cx", d => x(d[0]))
            .attr("cy", d => y(d[1]))
            .attr("r", 4)
            .attr("fill", "green");

        /* Plot all the sells as red dots */
        const sells = inner.selectAll("scatter-sells")
            .attr("clip-path", "url(#clipped-path)")
            .data(this.props.sells)
            .enter().append("svg:circle")
            .attr("cx", d => x(d[0]))
            .attr("cy", d => y(d[1]))
            .attr("r", 4)
            .attr("fill", "red");

        const focus = g.append("g")
            .attr("class", "focus")
            .style("display", "none");

        focus.append("circle")
            .attr("r", 4.5);

        focus.append("text")
            .attr("x", 9)
            .attr("dy", ".35em");

        inner.append("clipPath")
            .attr("id", "clipped-path")
            .append("rect")
            .attr("class", "overlay")
            .attr("width", width)
            .attr("height", height);

        const view = g.append("rect")
            .attr("pointer-events", "all")
            .attr("class", "overlay")
            .attr("width", width)
            .attr("height", height)
            .call(zoom);

        // svg.call(zoom);

        function zoomed() {
            const scale = d3.event.transform.k;

            inner.attr("transform", d3.event.transform);

            const xz = d3.event.transform.rescaleX(x);
            const yz = d3.event.transform.rescaleY(y);

            gX.call(xAxis.scale(d3.event.transform.rescaleX(x)));
            gY.call(yAxis.scale(d3.event.transform.rescaleY(y)));

            // closings.attr('d', line.x(d => xz(d[1])));
            // bollinger_upper.attr('d', indicator.x(d => xz(d)));
            // bollinger_lower.attr('d', indicator.x(d => xz(d)));
            // buys.attr('r', 1/scale * 4.5);
            // sells.attr('r', 1/scale * 4.5);

            closings.attr('stroke-width', 1/scale * 1.5);
            sma9.attr('stroke-width', 1/scale * 1.5);
            sma15.attr('stroke-width', 1/scale * 1.5);
            bollinger_upper.attr('stroke-width', 1/scale * 1.5);
            bollinger_lower.attr('stroke-width', 1/scale * 1.5);
            buys.attr('r', 1/scale * 4.5);
            sells.attr('r', 1/scale * 4.5);
        }
    }
}

export default Plot;